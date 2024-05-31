# gma/auth.py
import random
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from gma.models import User, Team, TeamUser, db
from gma.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

def generate_unique_team_name(email):
    base_name = email.split('@')[0]
    hash_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"{base_name}_{hash_suffix}"

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    team_code = request.args.get('team_code', '')

    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if form.team_code.data:
            # Join existing team as a regular user
            team = Team.query.filter_by(team_code=form.team_code.data).first()
            if team:
                team_user = TeamUser(user_id=user.id, team_id=team.id, role='regular')
                db.session.add(team_user)
                db.session.commit()
                flash('Successfully joined the team!', 'success')
            else:
                flash('Invalid team code', 'danger')
                return redirect(url_for('auth.register'))
        else:
            # Create a new team with a unique name and assign the user as admin
            team_name = generate_unique_team_name(user.email)
            team = Team(name=team_name)
            db.session.add(team)
            db.session.commit()

            team_user = TeamUser(user_id=user.id, team_id=team.id, role='admin')
            db.session.add(team_user)
            db.session.commit()
            flash('Team created and you are assigned as admin!', 'success')
        
        login_user(user)
        return redirect(url_for('controllers.index'))

    return render_template('register.html', form=form, team_code=team_code)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('controllers.index'))
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('controllers.index'))