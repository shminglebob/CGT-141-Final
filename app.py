from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import markdown

app = Flask(__name__)

# app.config['SERVER_NAME'] = 'paidvbux.com'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_page('index.html', 'home', request)

@app.route('/about')
def about():
    return render_page('about.html', 'about', request)

@app.route('/projects')
def projects():
    return render_page('projects.html', 'projects', request)

@app.route('/devlog')
def devlog():
    return render_page('devlog.html', 'devlog', request,
                           markdown_content=parse_md_file('static/md/Three Link Inverse Kinematics.md'))

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
    markdown_content = f'<h1 class="subtitle">{path.split("/")[-1][:-3]}</h1>'
    with open(path, 'r') as f:
        markdown_content += markdown.markdown(f.read(), extensions=['fenced_code', 'toc'])
        f.close()

    return markdown_content

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(host="0.0.0.0")
    app.run(debug=True)
