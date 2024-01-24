# main_app.py

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os
from json import JSONEncoder
from PIL import Image
from sketch import convert_to_sketch_and_save, label_device_with_resized_image
from sketch2 import convert_to_sketch, place_sketch_on_object
app = Flask(__name__)


# Configuration for SQLAlchemy, replace 'sqlite:///site.db' with your database connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
app.config['UPLOAD_FOLDER'] = './static/devices'
app.config['UPLOAD_FOLDER_NORMAL_USER'] = './static/user'
app.config['UPLOAD_FOLDER_SKETCH_USER'] = './static/sketches'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Allowed image file extensions


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # role = db.Column(db.String(60), nullable=False, default='user')

# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    # Add other fields as needed

class Devices(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(20), nullable=False)
    

class Sketches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.String(20), nullable=False)
    
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Devices):
            return obj.__dict__
        return super().default(obj)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Function to get the height and width of an image
def get_image_dimensions(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
    return width, height

# Routes

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, role='user')
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration Successful'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Your account could not created. Please try again'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    pass


## devices
@app.route('/fetch_devices', methods=['GET'])
@jwt_required()
def fetch_devices():
    devices = Devices.query.all()
    devices_list = [{'id': device.id, 'name': device.name, 
                     "image": device.image, 
                     'width': device.width, 'height': device.height} for device in devices]
    return jsonify({
        "devices": devices_list
    })


@app.route('/add_device', methods=['POST'])
@jwt_required()
def add_device():
    # data = request.get_json()
    current_user = get_jwt_identity()
    print(current_user)
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Check if the file has a valid filename and extension
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    # Save the uploaded file to the server
    filename = f"user_{current_user}_image_{file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(file_path)
    if not file.save(file_path) == "":
        width, height = get_image_dimensions(file_path)
        device = Devices(user_id=current_user, name=request.form.get('title'), width=width, height=height, image=filename)
        
        try:
            db.session.add(device)
            db.session.commit()
            return jsonify({'message': 'Device Add successfully', "Device": device})
        except Exception as e:
            print(e)
            return jsonify({'message': 'Image uploaded successfully'})
    else:
        return jsonify({'message': 'File could not be uploaded.'})


@app.route('/map_device/<int:device_id>', methods=['POST'])
@jwt_required()
def map_device(device_id):
    current_user = get_jwt_identity()
    
    #fetch device
    
    device = Devices.query.filter_by(id=device_id).first()
    if not device:
        return jsonify({'message': 'Device not found', 'status': False}), 400
    
    
    device_path = os.path.join(app.config['UPLOAD_FOLDER'], device.image)
    
    # data = request.get_json()

    # Check if the POST request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Check if the file has a valid filename and extension
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    # Save the uploaded file to the server
    filename = f"user_{current_user}_image_{file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER_NORMAL_USER'], filename)
    print(file_path)
    if not file.save(file_path) == "":
        label_image_path = convert_to_sketch(file_path)  
        output_path = label_image_path 
        scale_factor = 0.5  

        # Label the cup image with the resized label image and save the result
        place_sketch_on_object(label_image_path, device_path, app.config['UPLOAD_FOLDER_SKETCH_USER'])
        
        # width, height = get_image_dimensions(file_path)
        # device = Devices(user_id=current_user, name=request.form.get('title'), width=width, height=height, image=filename)
        
        # try:
        #     db.session.add(device)
        #     db.session.commit()
        #     return jsonify({'message': 'Device Add successfully', "Device": device})
        # except Exception as e:
        #     print(e)
        return jsonify({'message': 'Image uploaded successfully'})
    else:
        return jsonify({'message': 'File could not be uploaded.'})




@app.route('/place-order', methods=['POST'])
@jwt_required()
def place_order():
    current_user = get_jwt_identity()
    new_order = Order(user_id=current_user)
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order placed successfully'})

@app.route('/fetch-orders', methods=['GET'])
@jwt_required()
def fetch_orders():
    current_user = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user).all()
    return jsonify({'orders': [order.id for order in orders]})

# Add more routes for tracking orders, payment, admin panel, etc.

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
