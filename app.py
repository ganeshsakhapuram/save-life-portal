from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Donor
from twilio.rest import Client
import os
import logging

import random
from dotenv import load_dotenv  # Import dotenv to load environment variables
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from pymongo import MongoClient

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["blooddonation"]
donors_collection = db["donors"]
# Path to store registered users
DATA_FILE = "static/dashboard.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
@app.route('/')
def index():
    user_logged_in = session.get('user_logged_in', False)  # Example way to check login
    return render_template('index.html', user_logged_in=user_logged_in)

@app.route('/dashboard')
def dashboard():
   
    donors = list(donors_collection.find({}, {"_id": 0}))
    
    return render_template('dashboard.html', donors=donors)
# @app.route('/login')
# def login():
#     return render_template('login.html')  # Make sure login.html exists
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Dummy authentication, replace with database verification
        if email == "admin@example.com" and password == "admin":
            session['user_logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         blood_group = request.form.get('blood_group')
#         contact = request.form.get('contact')
#         password = request.form.get('password')

#         if not all([name, blood_group, contact, password]):
#             return render_template('register.html', error="Please fill in all fields.")

#         if not contact.isdigit() or len(contact) != 10:
#             return render_template('register.html', error="Invalid contact number. Please use a 10-digit number.")

#         new_donor = Donor(name=name, blood_group=blood_group, contact=contact)
#         new_donor.set_password(password)
#         db.session.add(new_donor)
#         db.session.commit()

#         return redirect(url_for('success'))
#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        blood_group = request.form.get('blood_group')
        location = request.form.get('location')
        contact = request.form.get('contact')
        
        if not all([name, blood_group, location, contact]):
            return render_template('register.html', error="Please fill in all fields.")
        
        donor = {"name": name, "blood_group": blood_group, "location": location, "contact": contact}
        print(donor,"naku e value teliyali puka")
        donors_collection.insert_one(donor)
        
        
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    return redirect(url_for('index'))
@app.route('/success')
def success():
    logging.debug("Success route accessed")
    return "Donor registered successfully!"
# Disable PyMongo debug logging
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.ERROR)
logging.getLogger("pymongo.connection").setLevel(logging.ERROR)


if __name__ == '__main__':
    app.run(debug=True)
