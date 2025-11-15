from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
import markdown
import json
import os

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

def parse_md_file(path):
    title = path.split("/")[-1][:-3]
    markdown_content = ''
    with open(path, 'r') as f:
        markdown_content += markdown.markdown(f.read(), extensions=['fenced_code', 'toc'])
        f.close()

    return title, markdown_content

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(host="0.0.0.0")
    app.run(debug=True)
