from functools import wraps
from flask import abort
from flask_login import current_user
from gma.models import TeamUser

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