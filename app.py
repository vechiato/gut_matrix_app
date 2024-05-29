from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import qrcode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User

login_manager = LoginManager(app)
login_manager.login_view = 'login'

def preload_data():
    # Check if the User table is empty
    if User.query.count() == 0:
        # Create a default user
        default_user = User(email="admin@example.com")
        default_user.set_password("admin123")
        db.session.add(default_user)
        db.session.commit()
        print("Default user created: admin@example.com")
    else:
        print("User table is not empty. No default user created.")

# Ensure database is created and preloaded
#@app.before_first_request
def initialize_database():
    db.create_all()
    preload_data()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes
from controllers import *

if __name__ == "__main__":
    app.run(debug=True)
