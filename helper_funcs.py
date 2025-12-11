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
    
    text = ''
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

prerendered_md = {}

projects_json = None

def init_md():
    # read from json
    with app.app_context():
        local_path = os.path.join(current_app.instance_path, 'projects.json')
        with open(local_path, 'r') as f:
            projects_json = json.loads(f.read())

    for slug in projects_json.keys():
        md_filename = projects_json[slug]['md-path']
        title, parsed_md = parse_md_file(f'static/md/{md_filename}')

        prerendered_md.update({ slug: (title, parsed_md) })
    
def fetch_md(slug):
    title, md = prerendered_md[slug] 
    return title, md