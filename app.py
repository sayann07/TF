from flask import Flask, request, jsonify, send_from_directory, session, render_template,  redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Pantua%402018@localhost:5432/TurfManager'  # Update with your actual database credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the database models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Turfs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    turf_id = db.Column(db.Integer, db.ForeignKey('turfs.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # Define a method to convert Booking object to JSON
    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'turf_id': self.turf_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
    
def authenticate_user(username, password):
    user = Users.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    else:
        return None
    

# Hosting the index.html
@app.route('/')
def serve_index():
    return render_template('index.html')


# API endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = Users(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username or email already exists'}), 400

# API endpoint to create a new turf
@app.route('/turfs', methods=['POST'])
def create_turf():
    data = request.json
    new_turf = Turfs(name=data['name'], location=data['location'], capacity=data['capacity'])
    db.session.add(new_turf)
    db.session.commit()
    return jsonify({'message': 'Turf created successfully'}), 201

# API endpoint to make a booking
@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    new_booking = Bookings(user_id=data['user_id'], start_time=datetime.fromisoformat(data['start_time']), end_time=datetime.fromisoformat(data['end_time']))
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Booking created successfully'}), 201

# API endpoint to get all bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Bookings.query.all()
    return jsonify([booking.to_json() for booking in bookings]), 200

if __name__ == '__main__':
    app.run(debug=True)
