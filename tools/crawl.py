#!/usr/bin/env python3
"""
Polite KB crawler for Nutrion.
- Respects robots.txt via urllib.robotparser
- Uses a clear User-Agent and retries
- Recursively resolves sitemaps; falls back to limited BFS crawl
- Extracts main content with trafilatura
- Saves Markdown files with YAML front matter into data/web/

Usage:
  python tools/crawl.py --site myplate --max-pages 40 --delay 2
  python tools/crawl.py --all
"""
import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

import requests
from requests.adapters import HTTPAdapter, Retry
import urllib.robotparser as rp
from bs4 import BeautifulSoup
import trafilatura

UA = "NutrionCrawler/0.1 (+https://github.com/zawlinnhtet03/nutrition-diet-assistant)"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "web")
DEFAULT_MAX_PAGES = 40
DEFAULT_DELAY = 2.0

@dataclass
class Site:
    key: str
    name: str
    base_url: str
    allow_patterns: List[str]
    deny_patterns: List[str]

SITES: List[Site] = [
    Site(
        key="myplate",
        name="USDA MyPlate",
        base_url="https://www.myplate.gov/",
        allow_patterns=[r"^/.*"],
        deny_patterns=[r"^/search", r"^/user", r"/login", r"/signup"],
    ),
    Site(
        key="harvard",
        name="Harvard Nutrition Source",
        base_url="https://www.hsph.harvard.edu/nutritionsource/",
        allow_patterns=[r"^/nutritionsource/.*"],
        deny_patterns=[r"/tag/", r"/category/", r"/author/"],
    ),
    Site(
        key="eatright",
        name="EatRight",
        base_url="https://www.eatright.org/",
        allow_patterns=[r"^/health/.*", r"^/food/.*"],
        deny_patterns=[r"/store", r"/cart", r"/login", r"/podcasts"],
    ),
    Site(
        key="who",
        name="WHO Nutrition",
        base_url="https://www.who.int/",
        allow_patterns=[
            r"^/health-topics/nutrition.*",
            r"^/news-room/fact-sheets/detail/.*",
            r"^/news-room/questions-and-answers/.*",
            r"^/publications/i/.*",
            r"^/nutrition/.*",
        ],
        deny_patterns=[r"/emergencies", r"/about/", r"/search", r"/login"],
    ),
    Site(
        key="fdc",
        name="FoodData Central",
        base_url="https://fdc.nal.usda.gov/",
        allow_patterns=[r"^/help/.*", r"^/about-us/.*"],
        deny_patterns=[r"^/fdc-app.html"],
    ),
]


def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    retries = Retry(total=5, backoff_factor=0.6, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def normalize_url(u: str) -> str:
    p = urlparse(u)
    # Drop fragment and most query params
    allowed_q = set()
    q = urlencode({k: v for k, v in parse_qsl(p.query) if k in allowed_q})
    return urlunparse((p.scheme, p.netloc, p.path.rstrip("/"), "", q, ""))


def matches_any(path: str, patterns: List[str]) -> bool:
    return any(re.search(p, path) for p in patterns)


def get_robots(base_url: str) -> rp.RobotFileParser:
    robots_url = urljoin(base_url, "/robots.txt")
    r = rp.RobotFileParser()
    try:
        r.set_url(robots_url)
        r.read()
    except Exception:
        pass
    return r


def extract_links(html: str, current_url: str) -> List[str]:
    try:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            links.append(urljoin(current_url, href))
        return links
    except Exception:
        return []


def sitemap_urls(session: requests.Session, base_url: str) -> List[str]:
    urls = set()
    candidates = [urljoin(base_url, "sitemap.xml"),
                  urljoin(base_url, "sitemap_index.xml"),
                  base_url.rstrip("/") + "/sitemap.xml"]

    for url in candidates:
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "xml")
            # Handle sitemap index
            for loc in soup.find_all("loc"):
                child = loc.text.strip()
                if child.endswith(".xml"):
                    urls.update(sitemap_urls(session, child))
                else:
                    urls.add(child)
        except Exception:
            continue
    return list(urls)



def extract_article(session: requests.Session, url: str, html: Optional[str] = None) -> Optional[dict]:
    try:
        # Prefer provided HTML to avoid an extra network call
        if html is None:
            try:
                resp = session.get(url, timeout=20)
                html = resp.text
            except Exception:
                return None
        
        # First try trafilatura for extraction
        data = trafilatura.extract(html, output="json", include_comments=False, include_tables=True)
        
        # If trafilatura fails, try manual extraction with BeautifulSoup
        if not data:
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string.strip()
            
            # Try to find main content
            main_content = None
            
            # WHO specific selectors
            if "who.int" in url:
                print(f"Processing WHO URL: {url}")
                for selector in [
                    "main", 
                    ".sf-content-block", 
                    ".content-block",
                    ".sf_colsIn",
                    "article",
                    ".content"
                ]:
                    content = soup.select_one(selector)
                    if content and len(content.get_text(strip=True)) > 200:
                        main_content = content
                        break
            
            # Generic selectors if WHO specific ones fail
            if not main_content:
                for selector in ["article", "main", ".content", ".post", ".entry", "#content", "#main"]:
                    content = soup.select_one(selector)
                    if content and len(content.get_text(strip=True)) > 200:
                        main_content = content
                        break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.body
            
            # Clean up the content
            if main_content:
                # Remove unwanted elements
                for element in main_content.select("script, style, nav, footer, header, .navigation, .search"):
                    element.decompose()
                
                text = main_content.get_text(separator='\n\n', strip=True)
                text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines
                
                if len(text) > 200:  # Only return if we have substantial content
                    return {"title": title or "Untitled", "text": text, "date": None}
            return None
        
        # Process trafilatura output
        j = json.loads(data)
        text = (j.get("text") or "").strip()
        title = (j.get("title") or "").strip()
        date = j.get("date") or j.get("date_publish")
        
        if len(text) < 100:
            return None
            
        return {"title": title or "Untitled", "text": text, "date": date}
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None


def save_markdown(doc: dict, source_name: str, url: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    slug = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    fname = f"{slug}.md"
    path = os.path.join(OUT_DIR, fname)
    front = {
        "title": doc.get("title", "Untitled"),
        "source": source_name,
        "url": url,
        "date": doc.get("date"),
        "tags": ["nutrition", "guidelines"],
    }
    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(json.dumps(front, ensure_ascii=False, indent=2))
        f.write("\n---\n\n")
        f.write(f"# {front['title']}\n\n")
        f.write(doc.get("text", ""))
    return path


def crawl_site(site: Site, max_pages: int, delay: float, sitemap_only: bool = False):
    session = build_session()
    robots = get_robots(site.base_url)
    base_netloc = urlparse(site.base_url).netloc

    # Special handling for WHO site which has specific nutrition pages
    if site.key == "who":
        seeds = [
            "https://www.who.int/health-topics/nutrition",
            "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
            "https://www.who.int/news-room/fact-sheets/detail/malnutrition",
            "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
            "https://www.who.int/news-room/questions-and-answers/item/nutrition-micronutrients",
            "https://www.who.int/news-room/questions-and-answers/item/nutrition",
            "https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding",
        ]
        print(f"Using {len(seeds)} predefined WHO nutrition URLs as seeds")
    else:
        # Collect seeds via sitemap; fallback to base URL
        seeds = sitemap_urls(session, site.base_url) or [site.base_url]

    visited: Set[str] = set()
    queue: List[str] = list(seeds)
    saved = 0

    while queue and saved < max_pages:
        url = queue.pop(0)
        url = normalize_url(url)
        if url in visited:
            continue
        visited.add(url)

        parsed = urlparse(url)
        if parsed.netloc != base_netloc:
            continue
        if not robots.can_fetch(UA, url):
            continue
        if site.allow_patterns and not matches_any(parsed.path, site.allow_patterns):
            continue
        if site.deny_patterns and matches_any(parsed.path, site.deny_patterns):
            continue

        try:
            resp = session.get(url, timeout=20)
        except Exception:
            continue
        if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
            continue

        article = extract_article(session, url, resp.text)
        if article:
            save_markdown(article, site.name, url)
            saved += 1

        # Only expand links when not in sitemap-only mode
        if not sitemap_only and (not seeds or seeds == [site.base_url]):
            for link in extract_links(resp.text, url):
                link_n = normalize_url(link)
                if link_n not in visited:
                    queue.append(link_n)

        time.sleep(delay)

    print(f"[{site.key}] Saved {saved} pages -> {OUT_DIR}")

    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=[s.key for s in SITES], help="Which site to crawl")
    parser.add_argument("--all", action="store_true", help="Crawl all predefined sites")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    parser.add_argument("--sitemap-only", action="store_true", help="Crawl only sitemap URLs; do not expand in-page links")
    args = parser.parse_args()

    targets = SITES if args.all else [s for s in SITES if s.key == args.site]
    if not targets:
        print("No site selected. Use --site or --all")
        return
    for site in targets:
        crawl_site(site, max_pages=args.max_pages, delay=args.delay, sitemap_only=args.sitemap_only)




if __name__ == "__main__":
    main()
