from post_reqs import *

with app.app_context():
    init_md()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(host="0.0.0.0")
    app.run(debug=True)
