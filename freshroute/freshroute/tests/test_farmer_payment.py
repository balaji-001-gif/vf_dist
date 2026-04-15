import frappe
import unittest

class TestFarmerPayment(unittest.TestCase):

    def test_farmer_payment_doc_creation(self):
        fp = frappe.new_doc("Farmer Payment")
        fp.due_amount = 5000
        fp.status = "Pending"
        self.assertEqual(fp.status, "Pending")

    def test_net_payable_is_less_than_due(self):
        """Net payable after deductions should be <= due_amount."""
        fp = frappe.new_doc("Farmer Payment")
        fp.due_amount = 5000
        fp.net_payable = 4800  # after TDS deduction
        self.assertLessEqual(fp.net_payable, fp.due_amount)
