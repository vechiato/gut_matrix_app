# gma/items.py
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from gma.models import User, Topic, Item, Vote, Team, TeamUser, db
from gma.utils import admin_required    

bp = Blueprint('items', __name__, url_prefix='/items')

@bp.route("/", methods=["GET"])
@login_required
def list_items():
    # Fetch all existing items for my team
    team_topics = Topic.query.join(TeamUser, Topic.team_id == TeamUser.team_id).filter(TeamUser.user_id == current_user.id).all()

    existing_topics = Topic.query.all()
    return render_template("items/list_items.html", topics=team_topics)

@bp.route("/get_items")
@login_required
def get_items():
    topic_id = request.args.get('topic_id')
    items = Item.query.filter_by(topic_id=topic_id).all()
    
    # Calculate priorities and sort items
    items_with_priority = [(item, item.calculate_priority()) for item in items]
    sorted_items = sorted(items_with_priority, key=lambda x: x[1], reverse=True)
    
    items_data = [{'id': item.id, 'name': item.name, 'priority': priority} for item, priority in sorted_items]
    return jsonify(items_data)

@bp.route("/create", methods=["GET", "POST"])
def create_item():
    if request.method == "POST":
        topic_id = request.form.get("topic_id")
        name = request.form.get("name")
        
        # Create a new item
        item = Item(name=name, topic_id=topic_id)
        db.session.add(item)
        db.session.commit()
        
        # After adding the item, reload the page
        return redirect(url_for('items.list_items'))

    items = Item.query.all()
    return render_template("items/create_item.html", items=items)

@bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == "POST":
        item.name = request.form.get("name")
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('items.list_items'))
    return render_template("items/edit_item.html", item=item)

@bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)

    # Check if the item has associated votes
    print(item.votes)
    if item.votes:
        print(item.votes)
        flash('Cannot delete topic with associated items!', 'error')
        return redirect(url_for('items.list_items'))

    # If no votes are associated with the item, proceed with deletion
    db.session.delete(item)
    db.session.commit()

    flash('Item deleted successfully', 'success')
    return redirect(url_for('items.list_items'))