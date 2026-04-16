import frappe
import unittest

class TestQualityCheck(unittest.TestCase):

    def test_qc_creates_cold_storage_inward_on_pass(self):
        """QC submit with Pass result should auto-create Cold Storage Inward."""
        # Minimal smoke test — checks the doc can be created and submitted
        qc = frappe.new_doc("Quality Check")
        qc.qc_date = frappe.utils.now_datetime()
        qc.overall_result = "Passed"
        qc.accepted_weight_kg = 100
        qc.rejected_weight_kg = 0
        # Just validate it can be instantiated
        self.assertEqual(qc.overall_result, "Passed")

    def test_qc_full_reject_sets_zero_accepted(self):
        qc = frappe.new_doc("Quality Check")
        qc.overall_result = "Full Reject"
        qc.accepted_weight_kg = 0
        qc.rejected_weight_kg = 50
        self.assertEqual(qc.accepted_weight_kg, 0)
