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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})

    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(public_id=secrets.token_hex(16), name=data['name'], password=hashed_password, admin=False)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.query.all()

    if not current_user.admin:
        return jsonify({'message': 'Access Denied!'})

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})


if __name__ == '__main__':
    app.run(debug=True)