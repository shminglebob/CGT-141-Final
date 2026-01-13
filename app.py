from post_reqs import *


if __name__ == '__main__':
    rendered_devlogs = [f for f in os.listdir('instance/devlog_cache') if os.path.isfile(os.path.join('instance/devlog_cache', f))]
    for devlog in rendered_devlogs:
        os.remove(os.path.join('instance/devlog_cache', devlog))
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)