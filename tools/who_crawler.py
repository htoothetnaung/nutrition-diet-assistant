#!/usr/bin/env python3
"""
WHO Nutrition Website Crawler

This script is specifically designed to crawl and extract content from WHO nutrition-related pages.
It saves the extracted content as markdown files in the data/web directory.
"""

import os
import re
import sys
import time
import hashlib
import requests
import frontmatter
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "web")
os.makedirs(DATA_DIR, exist_ok=True)

# WHO nutrition URLs to crawl
WHO_URLS = [
    "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
    "https://www.who.int/news-room/fact-sheets/detail/malnutrition",
    "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
    "https://www.who.int/health-topics/nutrition",
    "https://www.who.int/news-room/fact-sheets/detail/infant-and-young-child-feeding",
]

def download_page(url):
    """Download a web page and return its content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

def extract_who_content(html, url):
    """Extract content from WHO pages using specific selectors."""
    if not html:
        return None, None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title = None
    title_elem = soup.select_one("h1") or soup.select_one("title")
    if title_elem:
        title = title_elem.get_text(strip=True)
    
    # Try different selectors for WHO pages
    content_selectors = [
        "main",
        ".sf-detail-body-wrapper",
        ".sf-detail-body",
        ".sf_colsIn",
        "#PageContent_C006_Col00",
        "article",
        ".page-content"
    ]
    
    main_content = None
    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content and len(main_content.get_text(strip=True)) > 100:
            break
    
    if not main_content:
        print(f"No content found for {url}")
        return None, None
    
    # Remove unwanted elements
    for element in main_content.select("script, style, nav, footer, header, .navigation, .search, .sf-share"):
        element.decompose()
    
    # Extract structured content
    content_parts = []
    
    # Process headings and paragraphs
    for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
        if elem.name.startswith('h'):
            level = int(elem.name[1])
            text = elem.get_text(strip=True)
            if text:
                content_parts.append(f"\n{'#' * level} {text}\n")
        elif elem.name == 'p':
            text = elem.get_text(strip=True)
            if text:
                content_parts.append(text)
        elif elem.name in ['ul', 'ol']:
            list_items = []
            for li in elem.find_all('li'):
                li_text = li.get_text(strip=True)
                if li_text:
                    list_items.append(f"- {li_text}")
            if list_items:
                content_parts.append("\n".join(list_items))
        elif elem.name == 'table':
            # Simple table extraction
            table_text = []
            for row in elem.find_all('tr'):
                cells = []
                for cell in row.find_all(['th', 'td']):
                    cells.append(cell.get_text(strip=True))
                if cells:
                    table_text.append(" | ".join(cells))
            if table_text:
                content_parts.append("\n".join(table_text))
    
    # Join all content parts
    content = "\n\n".join(content_parts)
    
    # Clean up content
    content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
    
    if len(content) < 100:
        print(f"Content too short for {url}")
        return None, None
    
    return title, content

def save_markdown(url, title, content):
    """Save content as markdown file with YAML front matter."""
    if not content or not title:
        return False
    
    # Create filename from URL
    url_path = url.split('/')[-1]
    if not url_path or url_path == '':
        url_path = hashlib.md5(url.encode()).hexdigest()
    
    filename = f"who-{url_path}.md"
    filepath = os.path.join(DATA_DIR, filename)
    
    # Create front matter
    post = frontmatter.Post(
        content,
        title=title,
        source_url=url,
        date=datetime.now().strftime("%Y-%m-%d"),
        source="WHO",
        category="nutrition",
    )
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))
    
    print(f"Saved {url} to {filepath}")
    return True

def extract_links(html, base_url):
    """Extract links from HTML content."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        
        # Only include WHO nutrition-related URLs
        if ('who.int' in full_url and 
            ('nutrition' in full_url or 
             'diet' in full_url or 
             'food' in full_url or 
             'malnutrition' in full_url or
             'obesity' in full_url)):
            links.append(full_url)
    
    return links

def crawl_who_site(start_urls, max_pages=10, delay=1):
    """Crawl WHO site starting from given URLs."""
    visited = set()
    to_visit = list(start_urls)
    saved_count = 0
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        
        if url in visited:
            continue
        
        print(f"Processing {url}")
        visited.add(url)
        
        html = download_page(url)
        if not html:
            continue
        
        # Extract and save content
        title, content = extract_who_content(html, url)
        if title and content:
            if save_markdown(url, title, content):
                saved_count += 1
        
        # Extract links for further crawling
        links = extract_links(html, url)
        for link in links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)
        
        # Respect crawl delay
        time.sleep(delay)
    
    return saved_count

def main():
    """Main function to run the crawler."""
    max_pages = 20
    delay = 1
    
    print(f"Starting WHO nutrition crawler with {len(WHO_URLS)} seed URLs...")
    saved_count = crawl_who_site(WHO_URLS, max_pages, delay)
    print(f"Crawling complete. Saved {saved_count} pages to {DATA_DIR}")

if __name__ == "__main__":
    main()