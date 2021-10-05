import os
from app import create_app, db
from app.models import Role, User
from flask_migrate import Migrate


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def shell_context_processor():
    return dict(db=db, Role=Role, User=User)

@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
