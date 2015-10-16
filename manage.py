import os
from src import app
from src.models import db
from flask_script import Manager, prompt_bool
from flask_migrate import MigrateCommand

'''
database operations:

manage.py database create
manage.py database drop
manage.py database recreate
'''
db_manager = Manager(usage="Perform database operations")


@db_manager.command
def create():
    db.create_all()


@db_manager.command
def drop():
    if prompt_bool("Are you sure you want to lose all your data?"):
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


@test_manager.command
def models():
    os.system('nosetests tests/models_tests.py')


@test_manager.command
def controllers():
    os.system('nosetests tests/controllers_tests.py')


'''
Putting all the commands together into main manager
'''

manager = Manager(app)
manager.add_command('m', MigrateCommand)
manager.add_command('db', db_manager)
manager.add_command('test', test_manager)

if __name__ == '__main__':
    manager.run()
