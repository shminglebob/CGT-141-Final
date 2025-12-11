from database import *

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

    print('wow printed something!!!')

    local_path = os.path.join(app.instance_path, "projects.json")
    with open(local_path, "r", encoding="utf-8") as f:
        projects_json = json.load(f)

def _get_cache_path(slug: str) -> str:
    """
    disk cache path for a devlog:
    instance/devlog_cache/<slug>.html
    """
    cache_dir = os.path.join(app.instance_path, "devlog_cache")
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
    md_path = os.path.join(app.root_path, "static", "md", md_filename)

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

@app.route('/')
def index():
    return render_page('index.html', 'home', request)

@app.route('/about')
def about():
    return render_page('about.html', 'about', request)

@app.route('/projects')
def projects():
    import helper_funcs

    print(f'helper {helper_funcs.projects_json}')
    print(f'non-helper {projects_json}')

    ensure_projects_loaded()

    return render_page('projects.html', 'projects', request, projects_json=projects_json)

@app.route('/devlog')
@app.route('/devlog/')
def devlog_root():
    return redirect(url_for('projects'), code=301)

@app.route('/devlog/<slug>')
def devlog(slug):
    ensure_projects_loaded()
    theme = request.cookies.get('theme', 'light')

    if slug not in projects_json.keys():
        return render_template('error pages/page-not-found.html', theme=theme)

    title, parsed_md = fetch_md(slug)

    return render_template('skeletons/devlog-base.html', theme=theme, 
                           markdown_content=parsed_md, devlog_title=title)

@app.route('/contact')
def contact():
    return render_page('contact.html', 'contact', request)

@app.route('/gallery')
def gallery():
    return render_page('gallery.html', 'gallery', request)

@app.route('/resume')
def resume():
    return render_page('resume.html', 'resume', request)

def render_page(path, page_name, request, **kwargs):
    theme = request.cookies.get('theme', 'light')

    base_args = { 
        'theme' : theme, 
        'current_page' : page_name 
    }

    context = {**base_args, **kwargs}
    
    return render_template(path, **context)