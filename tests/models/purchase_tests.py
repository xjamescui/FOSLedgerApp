from tests import BaseTestCase
from src.models import User, Purchase, Membership


class PurchaseModelTestCase(BaseTestCase):
    email, account_id, price = 'james@test.com', 'abc123', 100

    def _create_purchase_with_membership_with_user(self):
        u = User.create(email=self.email, account_id=self.account_id)
        m = Membership.query.filter(Membership.user_id == u.id).first()
        p = Purchase.create(title='TEST', price=100, membership_id=m.id)
        return [p, m, u]

    def test_create_purchase_with_membership_with_user(self):
        p, m, u = self._create_purchase_with_membership_with_user()
        self.assertIsNotNone(p.date)
        assert m == p.membership == u.membership
        assert len(m.purchases) == 1
        assert m.purchases[0] == p

    def test_update_purchase(self):
        p, m, u = self._create_purchase_with_membership_with_user()
        assert p.price == self.price
        new_price = 77
        p.update(price=new_price)
        assert Purchase.get_by_id(p.id).price == p.price == new_price

    def test_delete_purchase(self):
        """
        Purchase deleted -> Membership NOT deleted -> User NOT deleted
        """
        p, m, u = self._create_purchase_with_membership_with_user()
        p.delete()
        assert Purchase.query.count() == 0
        assert not Purchase.get_by_id(p.id) and Membership.get_by_id(m.id) and User.get_by_id(u.id)
        assert len(m.purchases) == 0

    def test_delete_membership(self):
        """
        Membership deleted -> Purchase in that membership deleted -> User NOT deleted
        """
        p, m, u = self._create_purchase_with_membership_with_user()
        m.delete()
        assert not Purchase.get_by_id(p.id) and not Membership.get_by_id(m.id) and User.get_by_id(u.id)
        assert u.membership is None
