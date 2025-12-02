from database import *

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

SHIKI_CACHE = {}

def shiki_highlight_block(code, lang, theme):
    key = (code, lang, theme)
    if key in SHIKI_CACHE:
        return SHIKI_CACHE[key]

    payload = json.dumps({
        "code": code,
        "lang": lang,
        "theme": theme
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

    SHIKI_CACHE[key] = result.stdout
    return result.stdout

FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

def render_shiki(md_text, theme):
    def _repl(match):
        lang = match.group(1) or "text"
        code = match.group(2).rstrip("\n")
        return shiki_highlight_block(code, lang, theme)

    return FENCE_RE.sub(_repl, md_text)

def parse_md_file(path):
    title = path.split("/")[-1][:-3]
    
    text = ''
    with open(path, 'r') as f:
        text = f.read()

    text = replace_github_alerts(text)
    text = render_shiki(text, 'gruvbox-dark-soft')

    md = markdown.Markdown(extensions=[
            'admonition',
            'toc',
            'extra'])
    
    markdown_content = md.convert(text) 
    return title, markdown_content