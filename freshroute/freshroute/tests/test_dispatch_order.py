import frappe
import unittest

class TestDispatchOrder(unittest.TestCase):

    def test_dispatch_order_fields(self):
        do = frappe.new_doc("Dispatch Order")
        do.dispatch_date = frappe.utils.today()
        do.status = "Planned"
        self.assertEqual(do.status, "Planned")
        self.assertEqual(do.doctype, "Dispatch Order")

    def test_calculate_total_weight(self):
        do = frappe.new_doc("Dispatch Order")
        do.append("items_table", {"item_code": "Tomato", "quantity_kg": 50})
        do.append("items_table", {"item_code": "Onion", "quantity_kg": 30})
        do.calculate_total_weight()
        self.assertEqual(do.total_weight_kg, 80)
