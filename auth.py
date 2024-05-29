from app import app, db
from flask import request, jsonify
from models import User, Topic, Item

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    # Add user to the database
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return "User registered successfully"

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        return "Login successful"
    else:
        return "Invalid credentials"

