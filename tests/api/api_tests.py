from tests import BaseTestCase
from src.api import BaseResource


class BaseResourceTestCase(BaseTestCase):
    def test_sig_validation_is_correct(self):
        """
        Check that the hash check is correct
        """
        secret_key = '123'
        params = {
            'value': 100,
            'email': 'test@test.com',
            'account_id': 'aabacd'
        }
        expected_sig = 'c17c4744bced2ca181efdb4d7158f046'
        r = BaseResource()
        self.assertTrue(r.is_sig_valid(expected_sig, secret_key, params))

    def test_sig_validation_is_not_correct(self):
        """
        Check that the hash check is not correct
        """
        secret_key = '456'  # changed
        params = {
            'value': 100,
            'email': 'test@test.com',
            'account_id': 'aabacd'
        }
        expected_sig = 'c17c4744bced2ca181efdb4d7158f046'
        r = BaseResource()
        self.assertFalse(r.is_sig_valid(expected_sig, secret_key, params))
