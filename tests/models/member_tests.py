from tests import BaseTestCase
from src.models import User, Member


class MemberModelTestCase(BaseTestCase):
    email, account_id, secret_key = 'james@test.com', 'abc123', '123'

    def _create_user_with_membership(self):
        """
            Create a user and a member
        """
        u = User.create(account_id=self.account_id, secret_key=self.secret_key)
        m = Member.create(account_id=u.account_id, email=self.email)
        return [u, m]

    def test_create_user_with_membership(self):
        """
            Test user and membership relationship
        """
        self.assertEqual(User.query.count(), 0)
        self.assertEqual(Member.query.count(), 0)

        u, m = self._create_user_with_membership()

        self.assertEqual(User.query.count(), 1)
        self.assertEqual(Member.query.count(), 1)

        self.assertEqual(m.points, 0)
        self.assertEqual(m.credits, 0)
        self.assertEqual(m.purchases, [])

        self.assertEqual(u.members, [m])
        self.assertEqual(m.user, u)

    def test_update_membership(self):
        u, m = self._create_user_with_membership()
        m.update(points=100, credits=10)
        self.assertEqual(Member.get_by_id(m.id).points, 100)
        self.assertEqual(m.points, Member.get_by_id(m.id).points)
        self.assertEqual(Member.get_by_id(m.id).credits, 10)
        self.assertEqual(m.credits, 10)

    def test_points_to_credits(self):
        u,m = self._create_user_with_membership()
        m.update(points=100)
        m.convert_points_for(10)
        self.assertEqual(m.points, 0)
        self.assertEqual(m.credits, 10)

        m.update(points=100)
        m.convert_points_for(9999)  # should not be allowed
        self.assertEqual(m.points, 100)
        self.assertEqual(m.credits, 10)

    def test_delete_user_before_membership(self):
        """
        if user is deleted then user's membership should be deleted
        """
        u, m = self._create_user_with_membership()
        self.assertEqual(u.members, [m])
        self.assertIsNotNone(m)

        u.delete()
        self.assertIsNone(User.get_by_id(u.id))
        self.assertIsNone(Member.get_by_id(m.id))

    def test_delete_membership_before_user(self):
        """
             if user's membership is deleted then user should still exist
        """
        u, m = self._create_user_with_membership()
        self.assertIsNotNone(m)
        self.assertEqual(User.get_by_id(u.id).members, [m])

        m.delete()
        self.assertIsNone(Member.get_by_id(m.id))
        self.assertIsNotNone(User.get_by_id(u.id))
        self.assertEqual(User.get_by_id(u.id).members, [])
