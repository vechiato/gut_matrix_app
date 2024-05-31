# gma/topics.py
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from gma.models import User, Topic, Item, Vote, Team, TeamUser, db  

bp = Blueprint('topics', __name__, url_prefix='/topics')

@bp.route("/", methods=["GET", "POST"])
@login_required
def list_topics():
    team_topics = Topic.query.join(TeamUser, Topic.team_id == TeamUser.team_id).filter(
                                TeamUser.user_id == current_user.id).all()

    if request.method == 'POST':
        topic_id = request.form.get('topic_id')
        new_status = request.form.get('status')
        topic = Topic.query.get(topic_id)
        if topic:
            topic.status = new_status
            db.session.commit()
            return redirect(url_for('topics.list_topics'))

    return render_template("topics/list_topics.html", existing_topics=team_topics)

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_topic():
    if request.method == "POST":
        name = request.form.get("name")
        # Create a new topic
        topic = Topic(name=name, team_id=Team.query.join(TeamUser).filter(TeamUser.user_id == current_user.id).first().id )
        db.session.add(topic)
        db.session.commit()
        flash('Topic created successfully!', 'success')
        return redirect(url_for('topics.list_topics'))
    elif request.method == "GET":
        # Fetch all existing topics
        existing_topics = Topic.query.join(TeamUser, Topic.team_id == TeamUser.team_id).filter(
                                TeamUser.user_id == current_user.id).all()
        return render_template("topics/create_topic.html", existing_topics=existing_topics)
    return render_template("topics/create_topic.html")

@bp.route("/edit/<int:topic_id>", methods=["GET", "POST"])
@login_required
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == "POST":
        topic.name = request.form.get("name")
        db.session.commit()
        flash('Topic updated successfully!', 'success')
        return redirect(url_for('topics.list_topics'))
    return render_template("topics/edit_topic.html", topic=topic)

@bp.route("/delete/<int:topic_id>", methods=["POST"])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.options(joinedload(Topic.items)).get_or_404(topic_id)

    # Check if the topic has associated items
    if topic.items:
        print(topic.items)
        flash('Cannot delete topic with associated items!', 'error')
        return redirect(url_for('topics.list_topics'))

    # If no associated items, proceed with deletion
    db.session.delete(topic)
    db.session.commit()
    flash('Topic deleted successfully!', 'success')
    return redirect(url_for('topics.list_topics'))