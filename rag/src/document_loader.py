import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, DirectoryLoader, TextLoader, WebBaseLoader
from langchain_core.documents import Document
import frontmatter

def load_documents_from_sources(sources_config: List[Dict[str, Any]]):
    docs = []
    for source in sources_config:
        stype = source.get("type")
        if stype == "pdf" and (p := source.get("path")):
            if os.path.isdir(p):
                docs.extend(DirectoryLoader(p, glob="*.pdf", loader_cls=PyPDFLoader).load())
            elif os.path.isfile(p):
                docs.extend(PyPDFLoader(p).load())
        elif stype == "csv" and (p := source.get("path")) and os.path.isfile(p):
            docs.extend(CSVLoader(file_path=p, encoding="utf-8").load())
        elif stype == "text" and (p := source.get("path")):
            if os.path.isdir(p):
                docs.extend(DirectoryLoader(p, glob="*.txt", loader_cls=TextLoader).load())
            elif os.path.isfile(p):
                docs.extend(TextLoader(p).load())
        elif stype == "markdown" and (p := source.get("path")):
            # Load Markdown files with YAML front matter and convert to Documents
            file_paths: List[str] = []
            if os.path.isdir(p):
                for root, _, filenames in os.walk(p):
                    for fn in filenames:
                        if fn.lower().endswith(".md"):
                            file_paths.append(os.path.join(root, fn))
            elif os.path.isfile(p) and p.lower().endswith(".md"):
                file_paths.append(p)

            for fp in file_paths:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        post = frontmatter.load(f)
                    content = post.content or ""
                    meta = post.metadata or {}
                    # Always include path for traceability
                    meta.setdefault("source_path", fp)
                    # Normalize common metadata keys
                    if "title" in meta:
                        meta["title"] = str(meta["title"]).strip()
                    if "url" in meta:
                        meta["source"] = meta.get("source") or meta.get("domain") or meta.get("publisher")
                    docs.append(Document(page_content=content, metadata=meta))
                except Exception:
                    # Skip malformed files gracefully
                    continue
        elif stype == "website" and (urls := source.get("urls")):
            docs.extend(WebBaseLoader(web_paths=urls).load())
    return docs
