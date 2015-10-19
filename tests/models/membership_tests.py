from tests import BaseTestCase
from src.models import User, Membership


class MembershipModelTestCase(BaseTestCase):
    email, account_id = 'james@test.com', 'abc123'

    def _create_user_with_membership(self):
        """
            Create a user and a membership, associate membership to user
        """
        new_user = User.create(email=self.email, account_id=self.account_id)
        new_membership = Membership.query.filter(Membership.user_id == new_user.id).first()
        return [new_user, new_membership]

    def test_create_user_with_membership(self):
        """
            Test user and membership relationship
        """
        assert User.query.count() == Membership.query.count() == 0
        u, m = self._create_user_with_membership()
        assert User.query.count() == Membership.query.count() == 1
        assert User.get_by_id(u.id) and Membership.get_by_id(m.id)
        assert m.points == m.credits == 0
        assert m == u.membership
        assert u == m.user

    def test_update_membership(self):
        u, m = self._create_user_with_membership()
        m.update(points=100, credits=10)
        assert m.points == Membership.get_by_id(m.id).points == 100
        assert m.credits == 10

    def test_delete_user_before_membership(self):
        """
            if user is deleted then user's membership should be deleted
        """
        user, membership = self._create_user_with_membership()
        self.assertEqual(user.membership, membership)
        self.assertIsNotNone(membership)

        user.delete()
        self.assertIsNone(User.get_by_id(user.id))
        self.assertIsNone(Membership.get_by_id(membership.id))

    def test_delete_membership_before_user(self):
        """
             if user's membership is deleted then user should still exist
        """
        user, membership = self._create_user_with_membership()
        self.assertIsNotNone(membership)
        self.assertEqual(User.get_by_id(user.id).membership, membership)

        membership.delete()
        self.assertIsNone(Membership.get_by_id(membership.id))
        self.assertIsNotNone(User.get_by_id(user.id))
        self.assertIsNone(user.get_by_id(user.id).membership)
