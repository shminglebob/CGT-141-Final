from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
import subprocess, markdown, json, re, os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'poteto chip'

db = SQLAlchemy(app)

projects_json = None

# read from json
with app.app_context():
    local_path = os.path.join(current_app.instance_path, 'projects.json')
    with open(local_path, 'r') as f:
        projects_json = json.loads(f.read())


@app.route('/')
def index():
    return render_page('index.html', 'home', request)

@app.route('/about')
def about():
    return render_page('about.html', 'about', request)

@app.route('/projects')
def projects():
    return render_page('projects.html', 'projects', request, projects_json=projects_json)

@app.route('/devlog')
@app.route('/devlog/')
def devlog_root():
    return redirect(url_for('projects'), code=301)

@app.route('/devlog/<slug>')
def devlog(slug):
    theme = request.cookies.get('theme', 'light')

    if slug not in projects_json.keys():
        return render_template('error pages/page-not-found.html', theme=theme)

    curr_devlog = projects_json[slug]

    md_filename = curr_devlog['md-path']
    title, parsed_md = parse_md_file(f'static/md/{md_filename}')


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

github_alert_replacements = {
    '> [!important]' : '!!! important',
    '> [!warning]' : '!!! warning',
    '> [!note]' : '!!! note',
    '> [!tip]' : '!!! tip',
}

def replace_github_alerts(text):
    lines = text.splitlines()

    in_alert = False
    for i in range(len(lines)):
        l = lines[i].strip()
        if l[:4] == '> [!' and l[-1] == ']':
            lines[i] = github_alert_replacements[l]
            in_alert = True
            continue
        if in_alert and len(l) > 0: 
            if l[0] == '>':
                lines[i] = '\t' + l[1:]
            else:
                in_alert = False

    return '\n'.join(lines)

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
        capture_output=True
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")
    # app.run(debug=True)
