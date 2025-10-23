from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import markdown

app = Flask(__name__)

# Config (replace with your actual URI later)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/blog')
def blog():
    markdown_content = ''
    with open('static/md/Three Link Inverse Kinematics.md', 'r') as f:
        markdown_content = markdown.markdown(f.read())
        f.close()

    return render_template('blog.html', markdown_content=markdown_content)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")
