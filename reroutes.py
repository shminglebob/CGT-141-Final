from helper_funcs import *

@app.route('/')
def index():
    return render_page('index.html', 'home', request)

@app.route('/about')
def about():
    return render_page('about.html', 'about', request)

@app.route('/projects')
def projects():
    global projects_json    
    ensure_projects_loaded()

    return render_page('projects.html', 'projects', request, projects_json=projects_json)

@app.route('/devlog')
@app.route('/devlog/')
def devlog_root():
    return redirect(url_for('projects'), code=301)

@app.route('/devlog/<slug>')
def devlog(slug):
    global projects_json
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