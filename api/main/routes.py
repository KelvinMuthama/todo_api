import datetime
import jwt
from api import bcrypt
from api.models import User
from flask import request, jsonify, current_app, Blueprint

user_login = Blueprint('user_login', __name__)


@user_login.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})

    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW.Authenticate': 'Basic realm="Login required!"'})
