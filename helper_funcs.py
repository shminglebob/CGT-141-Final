from database import *
import os, json, subprocess, markdown, re
from flask import current_app

github_alert_replacements = {
    '> [!important]' : '!!! important',
    '> [!warning]' : '!!! warning',
    '> [!note]' : '!!! note',
    '> [!tip]' : '!!! tip',
}

def replace_github_alerts(text):
    lines = text.splitlines()
    for i, l in enumerate(lines):
        stripped = l.strip()
        if stripped in github_alert_replacements:
            lines[i] = github_alert_replacements[stripped]
    return "\n".join(lines)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHIKI_SCRIPT = os.path.join(BASE_DIR, "shiki_highlight.js")

def shiki_highlight_block(code, lang):
    payload = json.dumps({
        "code": code,
        "lang": lang,
        "theme": 'gruvbox-dark-soft'
    })

    result = subprocess.run(
        ["node", SHIKI_SCRIPT],
        input=payload,
        text=True,
        capture_output=True,
        timeout=2
    )

    if result.returncode != 0:
        escaped = (
            code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
        return f"<pre><code>{escaped}</code></pre>"

    return result.stdout

FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

def render_shiki(md_text):
    def _repl(match):
        lang = match.group(1) or "text"
        code = match.group(2).rstrip("\n")
        return shiki_highlight_block(code, lang)

    return FENCE_RE.sub(_repl, md_text)

def parse_md_file(path):
    title = path.split("/")[-1][:-3]

    with open(path, 'r') as f:
        text = f.read()

    text = replace_github_alerts(text)
    text = render_shiki(text)

    md = markdown.Markdown(extensions=[
        'admonition',
        'toc',
        'extra'])
    
    markdown_content = md.convert(text) 
    return title, markdown_content

# ---- lazy-loaded globals ----

projects_json = None
prerendered_md = {}

def ensure_projects_loaded():
    """load projects.json once, when first needed"""
    global projects_json
    if projects_json is not None:
        return

    local_path = os.path.join(current_app.instance_path, 'projects.json')
    with open(local_path, 'r') as f:
        projects_json = json.loads(f.read())

def ensure_md_loaded(slug):
    """ensure one devlog's markdown is parsed + cached"""
    global prerendered_md
    ensure_projects_loaded()

    if slug in prerendered_md:
        return

    if slug not in projects_json:
        raise KeyError(f"unknown devlog slug: {slug}")

    md_filename = projects_json[slug]['md-path']
    md_path = os.path.join(current_app.root_path, 'static', 'md', md_filename)
    title, parsed_md = parse_md_file(md_path)
    prerendered_md[slug] = (title, parsed_md)

def fetch_md(slug):
    ensure_md_loaded(slug)
    return prerendered_md[slug]
