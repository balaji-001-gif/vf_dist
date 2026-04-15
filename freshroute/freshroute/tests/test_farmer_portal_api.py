import frappe
import unittest

class TestFarmerPortalAPI(unittest.TestCase):

    def test_get_dashboard_data_returns_dict(self):
        from freshroute.api.farmer_portal import get_dashboard_data
        # Without a real farmer, expect a frappe.DoesNotExistError or similar
        # This test just checks the function is importable
        self.assertTrue(callable(get_dashboard_data))

    def test_get_procurements_is_callable(self):
        from freshroute.api.farmer_portal import get_procurements
        self.assertTrue(callable(get_procurements))

    def test_get_payments_is_callable(self):
        from freshroute.api.farmer_portal import get_payments
        self.assertTrue(callable(get_payments))

    def test_get_price_board_is_callable(self):
        from freshroute.api.farmer_portal import get_price_board
        self.assertTrue(callable(get_price_board))

    def test_update_profile_is_callable(self):
        from freshroute.api.farmer_portal import update_profile
        self.assertTrue(callable(update_profile))
