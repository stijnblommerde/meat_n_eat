import os
from app import create_app, db
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Request, Proposal, Date

COV = None
if os.environ.get('MEAT_N_EAT_COVERAGE'):
    import coverage
    # start coverage engine
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.environ.get('MEAT_N_EAT_CONFIG') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)

# Google web client authenticates port 5000
server = Server(host="0.0.0.0", port=5000)

# server runs on random free port
# server = Server(host="0.0.0.0", port='0')


def make_shell_context():
    return dict(app=app, db=db, User=User, Request=Request, Proposal=Proposal,
                Date=Date)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', server)


@manager.command
def test(coverage=False):
    """Run the unit tests"""
    if coverage and not os.environ.get('MEAT_N_EAT_COVERAGE'):
        import sys
        os.environ['MEAT_N_EAT_COVERAGE'] = '1'
        # restart module from top
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()

