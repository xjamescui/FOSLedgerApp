from tests import BaseTestCase
from src.models import User, Purchase, Member


class PurchaseModelTestCase(BaseTestCase):
    email, account_id, secret_key, price = 'james@test.com', 'abc123', '123', 100

    def _create_purchase_with_member_with_user(self):
        u = User.create(account_id=self.account_id, secret_key=self.secret_key)
        m = Member.create(email=self.email, account_id=u.account_id)
        p = Purchase.create(title='TEST', price=100, member_id=m.id)
        return [p, m, u]

    def test_create_purchase_with_member(self):
        p, m, u = self._create_purchase_with_member_with_user()
        self.assertIsNotNone(p.date)
        self.assertEqual(m.purchases, [p])

    def test_update_purchase(self):
        p, m, u = self._create_purchase_with_member_with_user()
        self.assertEqual(p.price, self.price)
        new_price = 77
        p.update(price=new_price)
        self.assertEqual(p.price, new_price)
        self.assertEqual(Purchase.get_by_id(p.id).price, new_price)

    def test_delete_purchase(self):
        """
        Purchase deleted -> Member NOT deleted -> User NOT deleted
        """
        p, m, u = self._create_purchase_with_member_with_user()
        p.delete()
        self.assertEqual(Purchase.query.count(), 0)
        assert not Purchase.get_by_id(p.id) and Member.get_by_id(m.id) and User.get_by_id(u.id)
        self.assertEqual(len(m.purchases), 0)

    def test_delete_membership(self):
        """
        Member deleted -> Purchases by that member deleted -> User NOT deleted
        """
        p, m, u = self._create_purchase_with_member_with_user()
        m.delete()
        self.assertIsNone(Purchase.get_by_id(p.id))
        self.assertIsNone(Member.get_by_id(m.id))
        self.assertIsNotNone(User.get_by_id(u.id))
        self.assertEqual(u.members, [])
