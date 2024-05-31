# gma/utils.py
from gma.models import Vote, TeamUser, Team
from flask_login import current_user

def calculate_priority(item):
    votes = Vote.query.filter_by(item_id=item.id).all()
    total_gravity = sum(vote.gravity for vote in votes)
    total_urgency = sum(vote.urgency for vote in votes)
    total_tendency = sum(vote.tendency for vote in votes)
    priority = total_gravity * total_urgency * total_tendency
    return priority


from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team_id = kwargs.get('team_id')
        team_user = TeamUser.query.filter_by(user_id=current_user.id, team_id=team_id).first()
        print(current_user.id, team_id, team_user)#, team_user.role)#, team_user.role)
        if not team_user or team_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
