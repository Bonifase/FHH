from flask import request, jsonify, make_response
import jwt
import datetime
from workout import app
from workout.models.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token,  decode_token
)


jwt = JWTManager(app)

blacklist = set()
stored_reset_tokens = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route("/user", methods=['GET'])
def get_users():

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['_id'] = user.id
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['email'] = user.email
        user_data['units'] = user.units
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})


@app.route("/user/<user_id>", methods=['GET'])
def get_user(user_id):

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'})

    user_data = {}
    user_data['_id'] = user.id
    user_data['first_name'] = user.first_name
    user_data['last_name'] = user.last_name
    user_data['email'] = user.email
    user_data['units'] = user.units
    user_data['admin'] = user.admin

    return jsonify({'users': user_data})


@app.route("/user", methods=['POST'])
def create_user():

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(
        first_name=data['first_name'], last_name=data['last_name'], password=hashed_password, email=data['email'], admin=False, units=data['units'])  # noqa

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': new_user.first_name + ' created'})


@app.route("/user/<user_id>", methods=['PUT'])
def promote_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'The user has been promoted to Admin'})


@app.route("/user/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': user.first_name + ' has heen deleted'})


@app.route("/login", methods=['POST'])
def login():

    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Provide login data'})

    user = User.query.filter_by(email=data.get('email')).first()

    if not user:
        return jsonify({'message': 'User not found'})

    if check_password_hash(user.password, data.get('password')):
        access_token = create_access_token(
                identity=user.id, expires_delta=datetime.timedelta(minutes=60))
        if access_token:
            response = {
                    'access_token': access_token,
                    'frist_name': user.first_name,
                    'last_name': user.last_name,
                    'admin': user.admin,
                    'userId': user.id,
                    'message': 'You logged in successfully.'
                }
            return jsonify(response), 200
    
    return jsonify({'message': 'Wrong Password'})

