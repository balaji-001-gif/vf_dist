import frappe
import unittest

class TestColdStorageInward(unittest.TestCase):

    def test_inward_doc_creation(self):
        csi = frappe.new_doc("Cold Storage Inward")
        csi.inward_date = frappe.utils.now_datetime()
        csi.temperature_at_arrival = 4.0
        self.assertIsNotNone(csi)
        self.assertEqual(csi.temperature_at_arrival, 4.0)

class TestColdStorageOutward(unittest.TestCase):

    def test_outward_doc_creation(self):
        cso = frappe.new_doc("Cold Storage Outward")
        cso.outward_date = frappe.utils.now_datetime()
        cso.temperature_at_dispatch = 5.0
        self.assertEqual(cso.temperature_at_dispatch, 5.0)
