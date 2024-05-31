import qrcode
from io import BytesIO
from flask import Response, current_app
from sqlalchemy.sql import func
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from gma.models import User, Team, TeamUser, Topic, Item, Vote, db
from gma.utils import calculate_priority

bp = Blueprint('controllers', __name__)

# Route definitions
@bp.route("/")
def index():
    user_count = User.query.count()
    my_team_count = 0
    topic_count = Topic.query.count()
    item_count = Item.query.count()
    vote_count = Vote.query.count()

    team_code = None
    qr_code_img = None

    print(current_user)

    if current_user.is_authenticated:
        team_user = TeamUser.query.filter_by(user_id=current_user.id).first()
        my_team_count = db.session.query(func.count(TeamUser.id)).filter(TeamUser.team_id.in_(
                    TeamUser.query.filter_by(user_id=current_user.id).with_entities(TeamUser.team_id))).scalar()
        if team_user:
            team_code = Team.query.join(TeamUser).filter(TeamUser.user_id == current_user.id).first().team_code
            qr_code_data = url_for('auth.register', _external=True) + '?team_code=' + team_code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,
                border=4,
            )
            qr.add_data(qr_code_data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            qr_code_img = BytesIO()
            img.save(qr_code_img)
            qr_code_img.seek(0)

    return render_template('index.html', user_count=user_count, topic_count=topic_count, item_count=item_count, 
                           vote_count=vote_count, team_code=team_code, qr_code_img=qr_code_img, my_team_count=my_team_count)

@bp.route("/qr_code")
def qr_code():
    team_user = TeamUser.query.filter_by(user_id=current_user.id).first()
    if not team_user:
        return "", 404
    
    team_code = Team.query.join(TeamUser).filter(TeamUser.user_id == current_user.id).first().team_code
    qr_code_data = url_for('auth.register', _external=True) + '?team_code=' + team_code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(qr_code_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_code_img = BytesIO()
    img.save(qr_code_img)
    qr_code_img.seek(0)
    return Response(qr_code_img, mimetype='image/png')


# @bp.route("/add_item", methods=["GET", "POST"])
# @login_required
# def add_item():
#     if request.method == "POST":
#         topic_id = request.form.get("topic_id")
#         name = request.form.get("name")
        
#         # Create a new item
#         item = Item(name=name, topic_id=topic_id)
#         db.session.add(item)
#         db.session.commit()
        
#         # After adding the item, reload the page
#         return redirect(url_for('controllers.add_item'))

#     topics = Topic.query.all()
#     return render_template("add_item.html", topics=topics)

# @bp.route("/get_items")
# @login_required
# def get_items():
#     topic_id = request.args.get('topic_id')
#     items = Item.query.filter_by(topic_id=topic_id).all()
    
#     # Calculate priorities and sort items
#     items_with_priority = [(item, item.calculate_priority()) for item in items]
#     sorted_items = sorted(items_with_priority, key=lambda x: x[1], reverse=True)
    
#     items_data = [{'id': item.id, 'name': item.name, 'priority': priority} for item, priority in sorted_items]
    return jsonify(items_data)

@bp.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    topic_id = request.args.get('topic_id', type=int)

    # Fetch active topics belonging to the user's teams that have items
    topics = (Topic.query
              .join(TeamUser, Topic.team_id == TeamUser.team_id)
              .filter(TeamUser.user_id == current_user.id, Topic.status == 'active')
              .order_by(Topic.created_at.desc())
              .all())

    # Filter topics to include only those with items
    topics = [topic for topic in topics if topic.items]

    # Select the most recent active topic with items by default
    selected_topic = topics[0] if topics else None

    if topic_id:
        selected_topic = Topic.query.get(topic_id)

    items = []
    user_votes = {}
    items_with_vote_count = []

    if selected_topic:
        items = Item.query.filter_by(topic_id=selected_topic.id).all()
        for item in items:
            votes_count = Vote.query.filter_by(item_id=item.id).count()
            items_with_vote_count.append({'item': item, 'votes_count': votes_count})

            user_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
            if user_vote:
                user_votes[item.id] = user_vote

    if request.method == 'POST':
        topic_id = request.form.get('topic_id')
        for item in items:
            gravity = request.form.get(f'gravity_{item.id}')
            urgency = request.form.get(f'urgency_{item.id}')
            tendency = request.form.get(f'tendency_{item.id}')
            if gravity and urgency and tendency:
                user_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
                if user_vote:
                    user_vote.gravity = gravity
                    user_vote.urgency = urgency
                    user_vote.tendency = tendency
                else:
                    new_vote = Vote(user_id=current_user.id, item_id=item.id, gravity=gravity, urgency=urgency, tendency=tendency)
                    db.session.add(new_vote)
        db.session.commit()
        return redirect(url_for('controllers.vote', topic_id=topic_id))

    return render_template('vote.html', topics=topics, selected_topic=selected_topic, items=items, 
                           user_votes=user_votes, items_with_vote_count=items_with_vote_count)


@bp.route("/generate_qr_code")
@login_required
def generate_qr_code():
    # Implementation
    pass

@bp.route("/calculate")
@login_required
def calculate():
    # Query all items from the database
    items = Item.query.all()

    # Calculate priority for each item
    prioritized_items = []
    for item in items:
        # Get all votes for the current item
        votes = Vote.query.filter_by(item_id=item.id).all()

        # Calculate total scores for gravity, urgency, and tendency
        total_gravity = sum(vote.gravity for vote in votes)
        total_urgency = sum(vote.urgency for vote in votes)
        total_tendency = sum(vote.tendency for vote in votes)

        # Calculate priority score using total scores
        priority_score = total_gravity * total_urgency * total_tendency

        # Append item and priority score to the list
        prioritized_items.append({
            "name": item.name,
            "priority_score": priority_score
        })

    # Sort items by priority score (highest to lowest)
    prioritized_items.sort(key=lambda x: x["priority_score"], reverse=True)

    # Return prioritized list of items as JSON response
    return jsonify(prioritized_items)

@bp.route('/results')
@login_required
def results():
    topic_id = request.args.get('topic_id')

    # Fetch topics belonging to the user's teams
    team_topics = Topic.query.join(TeamUser, Topic.team_id == TeamUser.team_id).filter(TeamUser.user_id == current_user.id).order_by(Topic.created_at.desc()).all()

    # Fetch topics belonging to the user's teams that have items
    team_topics = (Topic.query
              .join(TeamUser, Topic.team_id == TeamUser.team_id)
              .filter(TeamUser.user_id == current_user.id)
              .order_by(Topic.created_at.desc())
              .all())

    selected_topic = None
    items_with_priority = []

    if topic_id:
        selected_topic = Topic.query.get(topic_id)
    else:
        selected_topic = team_topics[0] if team_topics else None

    if selected_topic:
        # Fetch items for the selected topic along with their priority and votes count
        items = selected_topic.items
        for item in items:
            votes_count = db.session.query(func.count(Vote.id)).filter_by(item_id=item.id).scalar()
            priority = calculate_priority(item)  # Assuming you have a function to calculate priority
            items_with_priority.append({'item': item, 'votes_count': votes_count, 'priority': priority})
        
        # Sort items by priority in descending order
        items_with_priority.sort(key=lambda x: x['priority'], reverse=True)

    return render_template('results.html', topics=team_topics, selected_topic=selected_topic, items_with_priority=items_with_priority)
