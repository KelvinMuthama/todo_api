import datetime
import jwt
import secrets
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = '3d14af68bdf869190054c8be6fc44ccd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'

db = SQLAlchemy(app)

class User(db.model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

if __name__ == '__main__':
    app.run(debug=True)