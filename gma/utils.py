# gma/utils.py
from gma.models import Vote, TeamUser, Team
from flask_login import current_user

def calculate_priority(item):
    votes = Vote.query.filter_by(item_id=item.id).all()
    votes_count = len(votes)
    
    if votes_count == 0:
        return 0
    
    total_gravity = sum(vote.gravity for vote in votes)
    total_urgency = sum(vote.urgency for vote in votes)
    total_tendency = sum(vote.tendency for vote in votes)
    
    # Calculate average priority
    average_gravity = total_gravity / votes_count
    average_urgency = total_urgency / votes_count
    average_tendency = total_tendency / votes_count
    
    priority = average_gravity * average_urgency * average_tendency

    #print(votes_count, total_gravity, total_urgency, total_tendency, priority)    

    return priority

