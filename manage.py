import os
from src import app
from src.models import db, User
from flask_script import Manager

'''
database operations:

manage.py database create
manage.py database drop
manage.py database recreate
'''
db_manager = Manager(usage="Perform database operations")


@db_manager.command
def create():
    print "Creating tables..."
    db.create_all()

    print "Fixture: Creating Frontier's system account"
    if User.create(account_id='aabacd', secret_key='123', email='frontier@test.com'):
        print "Fixture: Create Success!"


@db_manager.command
def drop():
    print "Dropping tables..."
    db.drop_all()


@db_manager.command
def recreate():
    drop()
    create()


'''
test operations:

manage.py test all
manage.py test models
manage.py test controllers
'''

test_manager = Manager(usage="Run tests")


@test_manager.command
def all():
    os.system('nosetests')


'''
Putting all the commands together into main manager
'''

manager = Manager(app)
manager.add_command('db', db_manager)
manager.add_command('test', test_manager)

if __name__ == '__main__':
    manager.run()
