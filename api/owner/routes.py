import secrets
from api import db, bcrypt
from api.models import User
from flask import request, jsonify, Blueprint
from api.utils import token_required

owner = Blueprint('owner', __name__)


@owner.route('/user', methods=['POST'])
def create_user():

    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(
        data['password']).decode('utf-8')

    new_user = User(public_id=secrets.token_hex(
        16), name=data['name'], password=hashed_password, admin=False)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@owner.route('/user', methods=['GET'])
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

    return jsonify({'users': output})


@owner.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not current_user.admin:
        return jsonify({'message': 'Access Denied!'})

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})


@owner.route('/user/<public_id>', methods=['PUT'])
@token_required
def update_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Access Denied!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message': 'The user has been updated!'})


@owner.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Access Denied!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted'})
