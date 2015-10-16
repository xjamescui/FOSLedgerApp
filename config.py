import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'FOS.db')
SECRET_KEY = '\xb4\xea\x963\x1d\xeb\x7f\x87S\xfe*\x94\x11\x1c\xd7\x9d\xc8\xdeq|u\xc7a\xb7'

