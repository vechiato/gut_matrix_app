# GUT Matrix Web Application

## Overview
A collaborative GUT Matrix web application to prioritize items based on Gravity, Urgency, and Tendency.

## Features
- User Authentication
- Create and manage GUT Topics and Items
- Collaborative voting
- Real-time updates 
- Data visualization
- Export options (future)
- Mobile-friendly design

## Setup

### Requirements
- Python 3.11+
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Bcrypt
- Flask-WTF ...

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/vechiato/gut_matrix_app.git
   cd gut_matrix_app
   ```
2. Create a virtual environment: 
    ```bash
    python3 -m venv venv
    source venv/bin/activate  
    ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database
    ```bash
    export FLASH_APP=gma.py
    export FLASH_DEBUG=1
    export FLASK_RUN_PORT="5000" 
    export FLASK_RUN_HOST="0.0.0.0"

    flask db init
    flask db migrate 
    flask db upgrade
    ```

5. Run the application:
    ```bash
    flask run
    ```
## Usage

- Register as a new user or log in with an existing account.
- Create and manage GUT topics an items.
- Invite people to your team.
- Vote on items and view results.
