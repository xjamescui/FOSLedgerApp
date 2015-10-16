from flask_testing import TestCase
from src import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        return app

    def setUp(self):
        db.create_all()  # create all tables
        self.app = app
        self.client = self.app.test_client()  # used to test client AJAX calls

    def tearDown(self):
        db.session.remove()
        db.drop_all()  # delete or reset db tables
