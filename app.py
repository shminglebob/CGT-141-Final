from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import markdown

app = Flask(__name__)

app.config['SERVER_NAME'] = 'paidvbux.com:80'

# Config (replace with your actual URI later)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', subdomain='portfolio')
def index():
    return render_template('index.html', active_link='home')

@app.route('/about')
def about():
    return render_template('about.html', active_link='about')

@app.route('/projects')
def projects():
    return render_template('projects.html', active_link='projects')

@app.route('/devlog')
def devlog():
    return render_template('devlog.html', active_link='devlog', 
                           markdown_content=parse_md_file('static/md/Three Link Inverse Kinematics.md'))

@app.route('/contact')
def contact():
    return render_template('contact.html', active_link='contact')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', active_link='gallery')

@app.route('/resume')
def resume():
    return render_template('resume.html', active_link='resume')

def parse_md_file(path):
    markdown_content = f'<h1 class="subtitle">{path.split("/")[-1][:-3]}</h1>'
    with open(path, 'r') as f:
        markdown_content += markdown.markdown(f.read(), extensions=['fenced_code', 'toc'])
        f.close()

    return markdown_content

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")
    # app.run(debug=True)
