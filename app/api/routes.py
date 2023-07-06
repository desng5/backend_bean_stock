from flask import request
from . import api
from app import db
from ..models import User, Coffee
from .auth import basic_auth, token_auth
from ..routes import get_images

@api.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return {
        'token': token,
        'token_expiration': user.token_expiration
    }

@api.route('/coffees', methods=['GET'])
def get_coffees():
    coffees = db.session.execute(db.select(Coffee)).scalars().all()
    return [coffee.to_dict() for coffee in coffees]

@api.route('/users', methods=['POST'])
def create_user():
    if not request.is_json:
        return { 'error': 'Your request content-type must be application/json' }

    data = request.json
    required_fields = ['username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return { 'error': f"{', '.join(missing_fields)} fields are required" }, 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    check_user = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars().all()
    if check_user:
        return { 'error': 'User with that username and/or email already exists' }

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict()

@api.route('/me')
@token_auth.login_required
def get_me():
    user = token_auth.current_user()
    return user.to_dict()

@api.route('/coffees', methods=['POST'])
@token_auth.login_required
def create_coffee():
    if not request.is_json:
        return { 'error', 'Your request content-type must be application/json' }

    data = request.json
    required_fields = ['name', 'coffee_type', 'price', 'description', 'rating', 'brew_method', 'roaster']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return { 'error': f"{', '.join(missing_fields)} fields are required" }, 400

    name = data.get('name')
    coffee_type = data.get('coffee_type')
    price = data.get('price')
    description = data.get('description')
    rating = data.get('rating')
    brew_method = data.get('brew_method')
    roaster = data.get('roaster')
    image_url = get_images(name, coffee_type, roaster, brew_method, description)
    user = token_auth.current_user()

    new_coffee = Coffee(name=name, coffee_type=coffee_type, price=price, description=description, rating=rating, brew_method=brew_method, roaster=roaster, user_id=user.id, image_url=image_url)
    db.session.add(new_coffee)
    db.session.commit()
    return new_coffee.to_dict()

@api.route('/coffees/<coffee_id>', methods=['PUT'])
@token_auth.login_required
def edit_coffee(coffee_id):
    if not request.is_json:
        return { 'error': 'Your request content-type must be application/json' }
    coffee = db.session.get(Coffee, coffee_id)
    if coffee is None:
        return { 'error': f'Coffee with ID {coffee_id} does not exist' }, 404
    user = token_auth.current_user()
    if coffee.brewer != user:
        return { 'error': 'You do not have permission to edit this coffee' }, 403

    data = request.json
    for field in data:
        if field in { 'name', 'coffee_type', 'price', 'description', 'rating', 'brew_method', 'roaster' }:
            setattr(coffee, field, data[field])
    db.session.commit()
    return coffee.to_dict()

@api.route('/coffees/<coffee_id>', methods=['DELETE'])
@token_auth.login_required
def delete_coffee(coffee_id):
    coffee = db.session.get(Coffee, coffee_id)
    if coffee is None:
        return { 'error': f'Coffee with ID {coffee_id} does not exist' }, 404
    user = token_auth.current_user()
    if coffee.brewer != user:
        return { 'error': 'You do not have permission to edit this coffee' }, 403

    db.session.delete(coffee)
    db.session.commit()
    return { 'success': f'Your {coffee.name} coffee has been deleted' }