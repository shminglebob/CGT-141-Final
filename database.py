from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
import subprocess, markdown, json, re, os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'poteto chip'

db = SQLAlchemy(app)

class UserEmail(db.Model):
    __tablename__ = 'user_emails'

    email = db.Column(db.String, primary_key=True)

    def __repr__(self):
        return f'{self.email}'