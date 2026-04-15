import frappe
import unittest

class TestCustomerPortalAPI(unittest.TestCase):

    def test_create_order_callable(self):
        from freshroute.api.customer_portal import create_order
        self.assertTrue(callable(create_order))

    def test_get_order_status_callable(self):
        from freshroute.api.customer_portal import get_order_status
        self.assertTrue(callable(get_order_status))

    def test_get_price_list_callable(self):
        from freshroute.api.customer_portal import get_price_list
        self.assertTrue(callable(get_price_list))

    def test_integrations_endpoints_callable(self):
        from freshroute.api.integrations import (
            create_order, get_order_status,
            get_price_list, get_available_stock, cancel_order
        )
        for fn in [create_order, get_order_status, get_price_list,
                   get_available_stock, cancel_order]:
            self.assertTrue(callable(fn))
