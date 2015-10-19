from tests import BaseTestCase
from src.models import User


class UserModelTestCase(BaseTestCase):
    email, account_id = 'james@test.com', 'abc123'

    def _create_user(self):
        return User.create(email=self.email, account_id=self.account_id)

    def test_create_user(self):
        u = self._create_user()
        self.assertIsNotNone(u)
        self.assertEqual(u.id, 1)
        self.assertIsNotNone(u.membership, msg="should create membership along with new user")

    def test_update_user(self):
        u = self._create_user()
        new_account_id = 'abc456'
        u.update(account_id=new_account_id)
        self.assertEqual(User.get_by_id(u.id).account_id, new_account_id)

    def test_delete_user(self):
        u = self._create_user()
        u.delete()
        self.assertEqual(User.query.count(), 0)
        self.assertIsNone(User.get_by_id(u.id))
