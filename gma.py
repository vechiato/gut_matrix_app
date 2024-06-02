# run.py
import os
import click
from flask_migrate import Migrate
from gma import create_app
from .models import User, db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
