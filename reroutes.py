from helper_funcs import *

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