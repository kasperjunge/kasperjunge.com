#!/usr/bin/env python3
"""
Simple site builder - converts Markdown posts and HTML content to pages.

Usage:
    python build.py           # Build all pages and posts
    python build.py --watch   # Watch for changes and rebuild
    python build.py --serve   # Build and start local server
"""

import re
import time
import argparse
import threading
import http.server
import socketserver
from pathlib import Path
from datetime import datetime

import markdown
import frontmatter

# Configuration
POSTS_DIR = Path("posts")
CONTENT_DIR = Path("content")
TEMPLATES_DIR = Path("templates")
BLOG_DIR = Path("blog")
SITE_URL = "https://kasperjunge.com"


def load_template(name: str) -> str:
    """Load a template file."""
    return (TEMPLATES_DIR / name).read_text()


def render_template(template: str, context: dict) -> str:
    """
    Simple mustache-like template rendering.
    Supports: {{var}}, {{#var}}...{{/var}} for conditionals
    """
    # Handle conditional blocks {{#var}}...{{/var}}
    def replace_conditional(match):
        var_name = match.group(1)
        content = match.group(2)
        if context.get(var_name):
            # Replace nested {{var}} inside the block
            return re.sub(r'\{\{(\w+)\}\}', lambda m: str(context.get(m.group(1), '')), content)
        return ''
    
    result = re.sub(r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}', replace_conditional, template, flags=re.DOTALL)
    
    # Handle simple variable substitution {{var}}
    result = re.sub(r'\{\{(\w+)\}\}', lambda m: str(context.get(m.group(1), '')), result)
    
    return result


def format_date(date_obj) -> tuple[str, str]:
    """Return (ISO date, formatted date) from a date object."""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
    iso = date_obj.strftime("%Y-%m-%d")
    formatted = date_obj.strftime("%B %d, %Y").replace(" 0", " ")
    return iso, formatted


def parse_content_file(path: Path) -> tuple[dict, str, str]:
    """Parse a content file with frontmatter. Returns (metadata, content, scripts)."""
    text = path.read_text()
    
    # Check for scripts section
    scripts = ""
    if "---scripts---" in text:
        parts = text.split("---scripts---")
        text = parts[0]
        scripts = parts[1].strip() if len(parts) > 1 else ""
    
    # Parse frontmatter
    post = frontmatter.loads(text)
    return dict(post.metadata), post.content.strip(), scripts


def build_page(content_path: Path, base_template: str) -> None:
    """Build a static page from a content file."""
    metadata, content, scripts = parse_content_file(content_path)
    
    # Determine output path
    name = content_path.stem
    if name == "index":
        output_path = Path("index.html")
    else:
        output_dir = Path(name)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "index.html"
    
    # Build context
    nav_key = f"nav_{metadata.get('nav', '')}"
    context = {
        "title": metadata.get("title", "Kasper Junge"),
        "description": metadata.get("description", ""),
        "content": content,
        "scripts": scripts,
        nav_key: True,
    }
    
    html = render_template(base_template, context)
    output_path.write_text(html)
    print(f"  Built: {output_path}")


def build_post(md_path: Path, base_template: str) -> dict:
    """Build a blog post from Markdown. Returns post metadata."""
    post = frontmatter.load(md_path)
    
    # Extract metadata
    title = post.get("title", md_path.stem)
    slug = post.get("slug", md_path.stem)
    date = post.get("date", datetime.now())
    description = post.get("description", "")
    
    date_iso, date_formatted = format_date(date)
    
    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=["fenced_code", "tables"])
    content_html = md.convert(post.content)
    
    # Build article content
    article_content = f"""        <h1>{title}</h1>
        <div class="post-meta">{date_formatted}</div>

        <article>
{indent_html(content_html, 12)}
        </article>

        <footer>
            <a href="/blog/">← Back to blog</a>
        </footer>"""
    
    # Build context
    context = {
        "title": f"{title} — Kasper Junge",
        "description": description,
        "author": "Kasper Junge",
        "date": date_iso,
        "og_title": title,
        "og_description": description,
        "og_type": "article",
        "og_url": f"{SITE_URL}/blog/{slug}",
        "twitter_title": title,
        "twitter_description": description,
        "content": article_content,
        "nav_blog": True,
    }
    
    html = render_template(base_template, context)
    
    # Write to blog directory
    output_dir = BLOG_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(html)
    
    print(f"  Built: blog/{slug}/index.html")
    
    return {
        "title": title,
        "slug": slug,
        "date": date,
        "date_formatted": date_formatted,
        "description": description,
    }


def indent_html(html: str, spaces: int) -> str:
    """Indent HTML content."""
    indent = " " * spaces
    lines = html.split("\n")
    return "\n".join(indent + line if line.strip() else "" for line in lines)


def build_blog_index(posts: list[dict], base_template: str) -> None:
    """Build the blog index page."""
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    
    post_items = []
    for post in posts_sorted:
        post_items.append(
            f'            <li>\n'
            f'                <a href="/blog/{post["slug"]}/">{post["title"]}</a>\n'
            f'                <span class="date">{post["date_formatted"]}</span>\n'
            f'            </li>'
        )
    posts_html = "\n".join(post_items)
    
    content = f"""        <h1>Blog</h1>
        
        <ul class="post-list">
{posts_html}
        </ul>"""
    
    context = {
        "title": "Blog — Kasper Junge",
        "description": "Thoughts on AI, software engineering, and building things.",
        "content": content,
        "nav_blog": True,
    }
    
    html = render_template(base_template, context)
    
    index_path = BLOG_DIR / "index.html"
    index_path.write_text(html)
    print(f"  Built: blog/index.html")


def build_all():
    """Build all pages and posts."""
    print("Building site...")
    
    # Load base template
    base_template = load_template("base.html")
    
    # Build static pages
    if CONTENT_DIR.exists():
        for content_path in CONTENT_DIR.glob("*.html"):
            build_page(content_path, base_template)
    
    # Build blog posts
    posts = []
    if POSTS_DIR.exists():
        for md_path in POSTS_DIR.glob("*.md"):
            posts.append(build_post(md_path, base_template))
    
    # Build blog index
    if posts:
        build_blog_index(posts, base_template)
    
    print(f"Done! Built {len(list(CONTENT_DIR.glob('*.html')))} pages and {len(posts)} posts.")


def watch():
    """Watch for changes and rebuild."""
    print("Watching for changes... (Ctrl+C to stop)")
    last_build = time.time()
    
    watch_dirs = [POSTS_DIR, CONTENT_DIR, TEMPLATES_DIR, Path("static")]
    
    while True:
        try:
            latest_mtime = 0
            for watch_dir in watch_dirs:
                if watch_dir.exists():
                    for path in watch_dir.rglob("*"):
                        if path.is_file():
                            mtime = path.stat().st_mtime
                            if mtime > latest_mtime:
                                latest_mtime = mtime
            
            if latest_mtime > last_build:
                print("\nChange detected!")
                build_all()
                last_build = time.time()
            
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped watching.")
            break


def serve(port: int = 8000):
    """Start a local HTTP server."""
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Build site from templates and content")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch for changes")
    parser.add_argument("--serve", "-s", action="store_true", help="Start local server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Server port (default: 8000)")
    args = parser.parse_args()
    
    build_all()
    
    if args.serve:
        if args.watch:
            watch_thread = threading.Thread(target=watch, daemon=True)
            watch_thread.start()
        serve(args.port)
    elif args.watch:
        watch()


if __name__ == "__main__":
    main()
