# GUT Matrix Web Application

## Overview
A collaborative GUT Matrix web application to prioritize items based on Gravity, Urgency, and Tendency.

## Features
- User Authentication
- Create and manage GUT Topics
- Collaborative voting using the GUT Matrix
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
    export FLASH_APP=run.py
    export FLASH_DEBUG=1

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
License

This project is licensed under the MIT License.
