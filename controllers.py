from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Topic, Item, Vote
from forms import LoginForm, RegistrationForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import qrcode

# Route definitions
@app.route("/")
def index():
    user_count = User.query.count()
    topic_count = Topic.query.count()
    item_count = Item.query.count()
    vote_count = Vote.query.count()
    
    return render_template('index.html', user_count=user_count, topic_count=topic_count, item_count=item_count, vote_count=vote_count)


@app.route("/create_topic", methods=["GET", "POST"])
@login_required
def create_topic():
    if request.method == "GET":
        # Fetch all existing topics
        existing_topics = Topic.query.all()
        return render_template("create_topic.html", existing_topics=existing_topics)
    elif request.method == "POST":
        name = request.form.get("name")
        existing_topic_id = request.form.get("existing_topic_id")
        
        if existing_topic_id:
            # Use existing topic
            topic = Topic.query.get(existing_topic_id)
        else:
            # Create a new topic
            topic = Topic(name=name)
            db.session.add(topic)
            db.session.commit()
        
        return redirect(url_for('create_topic'))


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == 'POST':
        # Handle form submission to add a new item
        topic_id = request.form.get('topic_id')
        item_name = request.form.get('name')

        # Create a new item object and add it to the database
        topic = Topic.query.get(topic_id)
        if topic:
            new_item = Item(name=item_name, topic=topic)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('add_item'))

    elif request.method == "GET":
        existing_topics = Topic.query.all()
        return render_template("add_item.html", existing_topics=existing_topics)



# def add_item():
#     if request.method == "GET":
#         topics = Topic.query.all()

#         # Fetch items for the chosen topic (assuming topic_id is passed as a request parameter)
#         topic_id = request.args.get('topic_id')
#         if topic_id:
#             topic = Topic.query.get(topic_id)
#             items = topic.items.all()  # Fetch items for the chosen topic
#         else:
#             topic = None
#             items = None

#     #    return render_template("add_item.html", topics=topics)
#     elif request.method == "POST":
#         topic_id = request.form.get("topic_id")
#         name = request.form.get("name")
#         # Add item to the specified topic
#         item = Item(name=name, topic_id=topic_id)
#         db.session.add(item)
#         db.session.commit()
#     #    return "Item added successfully"
    
#     return render_template('add_item.html', topics=topics, topic=topic, items=items)

@app.route("/get_items")
@login_required
def get_items():
    topic_id = request.args.get('topic_id')
    items = Item.query.filter_by(topic_id=topic_id).all()
    items_data = [{'id': item.id, 'name': item.name} for item in items]
    return jsonify(items_data)

# @app.route("/vote_page")
# @login_required
# def vote_page():
#     items = Item.query.all()
#     topics = Topic.query.all()
#     user_id = current_user.id  # Get the logged-in user's ID
#     return render_template("vote.html", items=items, topics=topics, user_id=user_id)

from flask import request

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    topics = Topic.query.all()  # Fetch all topics
    if request.method == 'POST':
        topic_id = request.form.get('topic_id')
        # Get user's previous votes for the selected topic
        user_votes = {}  # Store user's votes for each item
        for item in Item.query.filter_by(topic_id=topic_id).all():
            user_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
            if user_vote:
                user_votes[item.id] = user_vote
            # Save or update user's vote for the item
            gravity = request.form.get('gravity_' + str(item.id))
            urgency = request.form.get('urgency_' + str(item.id))
            tendency = request.form.get('tendency_' + str(item.id))
            if gravity and urgency and tendency:
                if user_vote:
                    user_vote.gravity = gravity
                    user_vote.urgency = urgency
                    user_vote.tendency = tendency
                else:
                    user_vote = Vote(user_id=current_user.id, item_id=item.id, gravity=gravity, urgency=urgency, tendency=tendency)
                    db.session.add(user_vote)
        db.session.commit()
        # Redirect to the same page to avoid form resubmission
        return redirect('/vote?topic_id=' + topic_id)
    else:
        # Handle GET request
        selected_topic_id = request.args.get('topic_id')
        selected_topic = None
        items = []
        if selected_topic_id:
            selected_topic = Topic.query.get(selected_topic_id)
            items = Item.query.filter_by(topic_id=selected_topic_id).all()
            # Fetch user's previous votes for the selected topic
            user_votes = {}  # Store user's votes for each item
            for item in items:
                user_vote = Vote.query.filter_by(user_id=current_user.id, item_id=item.id).first()
                if user_vote:
                    user_votes[item.id] = user_vote
            return render_template('vote.html', topics=topics, selected_topic=selected_topic, items=items, user_votes=user_votes)
        else:
            return render_template('vote.html', topics=topics)

@app.route("/generate_qr_code")
@login_required
def generate_qr_code():
    # Implementation
    pass

@app.route("/calculate_priority")
@login_required
def calculate_priority():
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

def calculate_priority(item):
    # Fetch votes associated with the item
    votes = item.votes
    # Initialize variables to store total gravity, urgency, and tendency
    total_gravity = 0
    total_urgency = 0
    total_tendency = 0
    # Calculate total gravity, urgency, and tendency based on votes
    for vote in votes:
        total_gravity += vote.gravity
        total_urgency += vote.urgency
        total_tendency += vote.tendency
    # Calculate priority
    priority = total_gravity * total_urgency * total_tendency
    return priority


@app.route('/results')
@login_required
def results():
    topic_id = request.args.get('topic_id')
    topics = Topic.query.order_by(Topic.created_at.desc()).limit(15).all()  # Fetch all topics
    #last_five_topics = Topic.query.order_by(Topic.created_at.desc()).limit(5).all()
    selected_topic = None
    items_with_priority = []

    if topic_id:
        selected_topic = Topic.query.get(topic_id)
        if selected_topic:
            # Fetch items for the selected topic along with their priority and votes count
            items = selected_topic.items
            for item in items:
                votes_count = db.session.query(func.count(Vote.id)).filter_by(item_id=item.id).scalar()
                priority = calculate_priority(item)  # Assuming you have a function to calculate priority
                items_with_priority.append({'item': item, 'votes_count': votes_count, 'priority': priority})

    return render_template('results.html', topics=topics, selected_topic=selected_topic, items_with_priority=items_with_priority)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))