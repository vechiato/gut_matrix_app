# users_teams.py

from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import logging
from .models import db, User, Team, TeamUser

bp = Blueprint('users_teams', __name__)

def get_teams_attributions(current_user):
    """
    Determine if the current user is an admin and fetch the users they can manage.
    Returns:
        is_admin (bool): Whether the current user is an admin.
        manageable_users (list): List of users the current user can manage.
    """
    # Check if the current user has any admin role
    is_admin = any(team_user.role == 'admin' for team_user in current_user.team_users)
    
    admin_teams = [team_user.team for team_user in current_user.team_users if team_user.role == 'admin']
    regular_teams = [team_user.team for team_user in current_user.team_users if team_user.role != 'admin']

    if is_admin:
        admin_team_ids = [team_user.team_id for team_user in current_user.team_users if team_user.role == 'admin']
        # Get users who belong to any of the teams where the current user is an admin
        manageable_users = User.query.join(TeamUser).filter(TeamUser.team_id.in_(admin_team_ids)).all()
    else:
        manageable_users = [current_user]
    
    return is_admin, admin_teams, regular_teams, manageable_users

@bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_users_teams():
    if request.method == 'POST':
        pass

    users = User.query.all()
    teams = Team.query.all()

    is_admin, admin_teams, regular_teams, manageable_users = get_teams_attributions(current_user)

    return render_template('users_teams/manage.html', users=users, teams=teams, is_admin=is_admin, 
                           manageable_users=manageable_users, admin_teams=admin_teams, regular_teams=regular_teams)

@bp.route('/remove_user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    print(current_user, current_user.team_users)#, team_user.role)
    is_admin = any(team_user.role == 'admin' for team_user in current_user.team_users)
    print(is_admin)
    if is_admin:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('User has been removed successfully.', 'success')
        else:
            flash('User not found.', 'error')
    else:
        flash('You do not have permission to remove users.', 'error')
    return redirect(url_for('users_teams.manage_users_teams'))

@bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    print(request.method, user, current_user.id, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('users_teams.manage_users_teams'))
    
    is_admin, admin_teams, regular_teams, manageable_users = get_teams_attributions(current_user)
    if user_id not in [user.id for user in manageable_users]:
        flash('You do not have permission to edit this user.', 'error')
        return redirect(url_for('users_teams.manage_users_teams'))

    if request.method == 'POST':
        print(is_admin, manageable_users)
        if user_id in [user.id for user in manageable_users]:
            # Update user details based on form submission
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            
            db.session.commit()
            flash('User details updated successfully.', 'success') 
        else:
            flash('You do not have permission to edit this user.', 'error')
        
        return redirect(url_for('users_teams.manage_users_teams'))
    
    return render_template('users_teams/edit_user.html', user=user)

@bp.route('/user/create', methods=['POST'])
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if email or username already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            # Handle duplicate user creation error
            return "User already exists", 400

        # Create a new user
        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

    return redirect(url_for('users_teams.manage_users_teams'))

@bp.route('/team/create', methods=['GET','POST'])
def create_team():
    if request.method == 'POST':
        team_name = request.form.get('name')

        # Check if team name already exists
        existing_team = Team.query.filter_by(name=team_name).first()
        if existing_team:
            # Handle duplicate team creation error
            return "Team already exists", 400

        # Create a new team with a unique name and assign the user as admin
        #team_name = generate_unique_team_name(user.email)
        new_team = Team(name=team_name)
        db.session.add(new_team)
        db.session.commit()

        team_user = TeamUser(user_id=current_user.id, team_id=new_team.id, role='admin')
        db.session.add(team_user)
        db.session.commit()
        flash('Team created and you are assigned as admin!', 'success')

        return redirect(url_for('users_teams.manage_users_teams'))

    return render_template('users_teams/create_team.html')
