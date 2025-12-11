from database import *
import os
import json
import subprocess
import re
import markdown
from flask import current_app

# ----- github-style alert replacements -----

github_alert_replacements = {
    '> [!important]': '!!! important',
    '> [!warning]':  '!!! warning',
    '> [!note]':     '!!! note',
    '> [!tip]':      '!!! tip',
}

def replace_github_alerts(text: str) -> str:
    lines = text.splitlines()
    for i, l in enumerate(lines):
        stripped = l.strip()
        if stripped in github_alert_replacements:
            lines[i] = github_alert_replacements[stripped]
    return "\n".join(lines)

# ----- shiki integration -----

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHIKI_SCRIPT = os.path.join(BASE_DIR, "shiki_highlight.js")

def shiki_highlight_block(code: str, lang: str) -> str:
    payload = json.dumps({
        "code": code,
        "lang": lang,
        "theme": "gruvbox-dark-soft"
    })

    # this is the expensive part – we want to call this as rarely as possible
    result = subprocess.run(
        ["node", SHIKI_SCRIPT],
        input=payload,
        text=True,
        capture_output=True,
        timeout=5  # you can keep 2 if you want, 5 is a bit safer
    )

    if result.returncode != 0:
        # fallback: no highlighting, just safe-escaped code
        escaped = (
            code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
        return f"<pre><code>{escaped}</code></pre>"

    return result.stdout

FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

def render_shiki(md_text: str) -> str:
    def _repl(match: re.Match) -> str:
        lang = match.group(1) or "text"
        code = match.group(2).rstrip("\n")
        return shiki_highlight_block(code, lang)

    return FENCE_RE.sub(_repl, md_text)

# ----- markdown parsing -----

def parse_md_file(path: str):
    # derive title from filename (no extension)
    title = os.path.splitext(os.path.basename(path))[0]

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    text = replace_github_alerts(text)
    text = render_shiki(text)

    md = markdown.Markdown(extensions=["admonition", "toc", "extra"])
    markdown_content = md.convert(text)

    return title, markdown_content

# ----- lazy-loaded project + devlog cache -----

projects_json = None       # loaded once from instance/projects.json
prerendered_md = {}        # in-memory cache: slug -> (title, html)

def ensure_projects_loaded():
    """load instance/projects.json once per worker, when first needed."""
    global projects_json

    if projects_json is not None:
        return

    local_path = os.path.join(current_app.instance_path, "projects.json")
    with open(local_path, "r", encoding="utf-8") as f:
        projects_json = json.load(f)

def _get_cache_path(slug: str) -> str:
    """
    disk cache path for a devlog:
    instance/devlog_cache/<slug>.html
    """
    cache_dir = os.path.join(current_app.instance_path, "devlog_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{slug}.html")

def ensure_md_loaded(slug: str):
    """
    make sure markdown for this slug is available in memory.
    order:
      1) ensure projects.json is loaded
      2) if already in prerendered_md -> done
      3) if cached html exists on disk -> load and store in prerendered_md
      4) otherwise -> parse markdown, run shiki, write html to disk, cache in memory
    """
    global prerendered_md
    ensure_projects_loaded()

    if slug in prerendered_md:
        return

    if slug not in projects_json:
        raise KeyError(f"unknown devlog slug: {slug}")

    cache_path = _get_cache_path(slug)
    md_filename = projects_json[slug]["md-path"]
    md_path = os.path.join(current_app.root_path, "static", "md", md_filename)

    # 1) disk cache hit → just read html
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            parsed_md = f.read()

        # title derived from md filename to stay consistent
        title = os.path.splitext(os.path.basename(md_filename))[0]
        prerendered_md[slug] = (title, parsed_md)
        return

    # 2) no cache → do the expensive path once
    title, parsed_md = parse_md_file(md_path)

    # write html to disk cache so other workers don't rerun shiki
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(parsed_md)

    prerendered_md[slug] = (title, parsed_md)

def fetch_md(slug: str):
    """
    public api for routes:
       title, html = fetch_md(slug)
    """
    ensure_md_loaded(slug)
    return prerendered_md[slug]
