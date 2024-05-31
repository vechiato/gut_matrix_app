from gma import db
import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    team_code = db.Column(db.String(6), unique=True, nullable=False, default=lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=6)))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', secondary='team_user', back_populates='teams')
    topics = db.relationship('Topic', backref='team', lazy=True)

class TeamUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    role = db.Column(db.String(50), default='regular' , nullable=False)  # 'admin' or 'regular'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def role(self, role):
        return '<Role %r>' % role

    __table_args__ = (db.UniqueConstraint('user_id', 'team_id', name='_user_team_uc'),)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, index=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)

    teams = db.relationship('Team', secondary='team_user', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), default='active' , nullable=False)  # 'active' or 'inactive'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    items = db.relationship('Item', backref='topic', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
 
    def calculate_priority(self):
        gravity_sum = sum(vote.gravity for vote in self.votes)
        urgency_sum = sum(vote.urgency for vote in self.votes)
        tendency_sum = sum(vote.tendency for vote in self.votes)
        
        # Assuming we want to use the average of votes for the priority calculation
        vote_count = len(self.votes)
        if vote_count == 0:
            return 0
        
        gravity_avg = gravity_sum / vote_count
        urgency_avg = urgency_sum / vote_count
        tendency_avg = tendency_sum / vote_count
        
        return gravity_avg * urgency_avg * tendency_avg 

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gravity = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.Integer, nullable=False)
    tendency = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lastupdated_at = db.Column(db.DateTime, default=datetime.utcnow)

    item = db.relationship('Item', backref=db.backref('votes', lazy=True))
    user = db.relationship('User', backref=db.backref('votes', lazy=True))    

    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),)