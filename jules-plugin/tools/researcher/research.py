#!/usr/bin/env python3
"""
Generalized Researcher Tool
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

try:
    import httpx
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
    from rich.console import Console
    from rich.table import Table
    import rich.box as box
except ImportError:
    print("Dependencies missing. Please install from requirements.txt", file=sys.stderr)
    sys.exit(1)

console = Console()

def get_cache_dir(args):
    if args.cache_dir:
        return os.path.abspath(args.cache_dir)
    env_cache = os.environ.get("JULES_RESEARCH_CACHE")
    if env_cache:
        return os.path.abspath(env_cache)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')

def get_index_file(cache_dir):
    return os.path.join(cache_dir, 'index.json')

def load_index(cache_dir):
    index_file = get_index_file(cache_dir)
    if not os.path.exists(index_file):
        return {}
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_index(cache_dir, index):
    os.makedirs(cache_dir, exist_ok=True)
    with open(get_index_file(cache_dir), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

def _find_entry(index, query):
    for h, entry in index.items():
        if entry.get('label') == query or entry.get('url') == query or h.startswith(query):
            return h, entry
    return None, None

def fetch(args):
    url = args.url
    cache_dir = get_cache_dir(args)
    os.makedirs(cache_dir, exist_ok=True)
    
    try:
        with httpx.Client(follow_redirects=True, timeout=15.0) as client:
            resp = client.get(url, headers={'User-Agent': 'Mozilla/5.0 (Researcher Bot)'})
            resp.raise_for_status()
            content_type = resp.headers.get('Content-Type', 'text/plain').lower()
            data = resp.read()
    except Exception as e:
        console.print(f"[red]Failed to fetch {url}: {e}[/red]", style="bold")
        sys.exit(1)

    sha256 = hashlib.sha256(data).hexdigest()
    
    filename_raw = f"{sha256}.raw"
    filename_md = f"{sha256}.md"
    
    filepath_raw = os.path.join(cache_dir, filename_raw)
    filepath_md = os.path.join(cache_dir, filename_md)

    with open(filepath_raw, 'wb') as f:
        f.write(data)

    parsed_len = 0
    if 'html' in content_type:
        soup = BeautifulSoup(data, 'html.parser')
        
        # Remove script and style elements completely
        for script_or_style in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            script_or_style.decompose()
            
        cleaned_html = str(soup)
        markdown_text = md(cleaned_html, heading_style="ATX").strip()
        parsed_len = len(markdown_text.encode('utf-8'))
        
        with open(filepath_md, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
    else:
        # For non-HTML, just write text
        with open(filepath_md, 'wb') as f:
            f.write(data)
        parsed_len = len(data)

    index = load_index(cache_dir)
    now = datetime.now(timezone.utc).isoformat()
    
    entry = {
        'url': url,
        'fetched_at': now,
        'label': args.label,
        'content_type': content_type,
        'bytes_raw': len(data),
        'bytes_md': parsed_len,
        'file_raw': filename_raw,
        'file_md': filename_md
    }
    
    index[sha256] = entry
    save_index(cache_dir, index)
    
    console.print(f"[green]Fetched {url} -> {sha256[:8]}[/green] (raw: {len(data)}b, md: {parsed_len}b)")

def list_entries(args):
    cache_dir = get_cache_dir(args)
    index = load_index(cache_dir)
    
    if not index:
        console.print("No entries in cache.")
        return
        
    table = Table(title="Cached Documents", box=box.SIMPLE)
    table.add_column("Hash", style="cyan", no_wrap=True)
    table.add_column("Label", style="magenta")
    table.add_column("URL", style="blue")
    table.add_column("Size (MD)", justify="right")
    table.add_column("Fetched At")
    
    for h, entry in index.items():
        label = entry.get('label') or '-'
        url = entry.get('url') or ''
        if len(url) > 50:
            url = url[:47] + '...'
        size = f"{entry.get('bytes_md', 0) // 1024} KB"
        fetched = entry.get('fetched_at', '')[:19].replace('T', ' ')
        table.add_row(h[:8], label, url, size, fetched)
        
    console.print(table)

def read_entry(args):
    cache_dir = get_cache_dir(args)
    index = load_index(cache_dir)
    h, entry = _find_entry(index, args.query)
    
    if not h:
        console.print(f"[red]Not found: {args.query}[/red]")
        sys.exit(1)
        
    filename = entry['file_raw'] if args.raw else entry['file_md']
    filepath = os.path.join(cache_dir, filename)
    
    if not os.path.exists(filepath):
        console.print(f"[red]Cache file missing: {filepath}[/red]")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        print(content)

def search_entries(args):
    cache_dir = get_cache_dir(args)
    index = load_index(cache_dir)
    query_str = args.query.lower()
    
    for h, entry in index.items():
        filepath = os.path.join(cache_dir, entry['file_md'])
        if not os.path.exists(filepath):
            continue
            
        display_name = entry.get('label') or h[:8]
        
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if query_str in line.lower():
                    clean_line = line.strip()
                    if len(clean_line) > 100:
                        clean_line = clean_line[:97] + '...'
                    # Token efficiency: compact output
                    print(f"{display_name}:{i+1}:{clean_line}")

def summarize_entry(args):
    cache_dir = get_cache_dir(args)
    index = load_index(cache_dir)
    h, entry = _find_entry(index, args.query)
    
    if not h:
        console.print(f"[red]Not found: {args.query}[/red]")
        sys.exit(1)
        
    filepath = os.path.join(cache_dir, entry['file_md'])
    if not os.path.exists(filepath):
        console.print(f"[red]Cache file missing: {filepath}[/red]")
        sys.exit(1)
        
    if args.full:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            print(f.read())
        return

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    lines = content.split('\n')
    h1 = "No Heading Found"
    first_p = "No Paragraph Found"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('# ') and h1 == "No Heading Found":
            h1 = line
        elif not line.startswith('#') and first_p == "No Paragraph Found":
            first_p = line
            
        if h1 != "No Heading Found" and first_p != "No Paragraph Found":
            break
            
    console.print(f"[bold cyan]{entry.get('label') or h[:8]}[/bold cyan]")
    console.print(f"URL: {entry.get('url')}")
    console.print(f"Heading: {h1}")
    console.print(f"Summary: {first_p}")
    if len(content) > 500:
         console.print("\n[dim]Note: Use --full for full content.[/dim]")

def main():
    parser = argparse.ArgumentParser(description="Researcher Tool. Token efficient cache interface.")
    parser.add_argument("--cache-dir", help="Override default cache directory")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a URL and cache it (Worst case size: ~100 bytes stdout)")
    fetch_parser.add_argument("url")
    fetch_parser.add_argument("--label", help="Label for this document")
    
    list_parser = subparsers.add_parser("list", help="List cached items (Worst case size: ~1KB per 10 items)")
    
    read_parser = subparsers.add_parser("read", help="Read a cached file (Worst case size: Entire markdown content. Warning: High token usage)")
    read_parser.add_argument("query", help="Label, URL, or hash")
    read_parser.add_argument("--raw", action="store_true", help="Return raw HTML instead of parsed Markdown")
    
    search_parser = subparsers.add_parser("search", help="Search inside markdown cache (Worst case size: ~100 bytes per match)")
    search_parser.add_argument("query", help="Text to search for")
    
    sum_parser = subparsers.add_parser("summarize", help="Summarize a document (Worst case size: ~500 bytes. High efficiency)")
    sum_parser.add_argument("query", help="Label, URL, or hash")
    sum_parser.add_argument("--full", action="store_true", help="Return the full markdown content instead of summary")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        fetch(args)
    elif args.command == "list":
        list_entries(args)
    elif args.command == "read":
        read_entry(args)
    elif args.command == "search":
        search_entries(args)
    elif args.command == "summarize":
        summarize_entry(args)

if __name__ == "__main__":
    main()
