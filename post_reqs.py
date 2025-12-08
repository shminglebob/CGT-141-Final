from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from reroutes import *
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'jiangjeric@gmail.com'   
app.config['MAIL_PASSWORD'] = 'bozg eekk vles rwhu'
app.config['MAIL_DEFAULT_SENDER'] = 'jiangjeric@gmail.com'

mail = Mail(app)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')

    email_entry = UserEmail(email=email)

    try:
        db.session.add(email_entry)
        db.session.commit()

        msg = Message('Subscribed to paidvbux\'s Newsletter!', recipients=[email])
        msg.body = 'Thank you for subscribing to my newsletter! You will receive updates whenever I post a new devlog!'

        mail.send(msg)
    except IntegrityError:
        db.session.rollback()
        return {'result':'error', 'error':'user exists'}, 409
    except Exception:
        db.session.rollback()
        return {'result':'error', 'error':'unknown exists'}, 500

    return {'result':'success'}, 201

@app.route('/contact-form', methods=['POST'])
def send_contact_form():
    data = request.json

    header = f'{data.get("reason").capitalize()} Opportunity from {data.get("company")}'
    email_content = f'{data.get("message")}\nFrom {data.get("name")}, \n{data.get("email")}'
    
    msg = Message(header, recipients=['jiangjeric@gmail.com'])
    msg.body = email_content

    mail.send(msg)

    return 'success'