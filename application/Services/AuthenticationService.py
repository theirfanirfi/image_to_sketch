from application.models.User import User
from app import bcrypt
from flask import jsonify
from app import db


class AuthenticationService:
    def __init__(self) -> None:
        pass
    
    def register_user(self, data):
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'})