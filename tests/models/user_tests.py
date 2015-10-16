from tests import BaseTestCase
from src.models import User


class UserModelTestCase(BaseTestCase):
    email, account_id = 'james@test.com', 'abc123'

    # all methods beginning with "test_" will be recognized by test runner
    def test_user(self):
        self.assertEqual(User.query.count(), 0)

        # create user
        new_user = User.create(email=self.email, account_id=self.account_id)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(new_user.id, 1)
        self.assertEqual(User.get_by_id(1), new_user)

        # update user
        new_account_id = 'abc456'
        new_user.update(account_id=new_account_id)
        self.assertEqual(User.get_by_id(new_user.id).account_id, new_account_id)

        # delete user
        new_user.delete()
        self.assertEqual(User.query.count(), 0)
        self.assertIsNone(User.get_by_id(new_user.id))