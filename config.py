import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'FOS.db')


