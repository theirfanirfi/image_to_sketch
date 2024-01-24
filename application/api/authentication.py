from flask import request, jsonify
from app import app
# from app import bcrypt
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data['username']).first()

#     if user and bcrypt.check_password_hash(user.password, data['password']):
#         access_token = create_access_token(identity=user.id)
#         return jsonify(access_token=access_token)
#     else:
#         return jsonify({'message': 'Invalid credentials'}), 401