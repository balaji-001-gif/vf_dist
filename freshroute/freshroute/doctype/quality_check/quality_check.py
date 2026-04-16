import frappe
from frappe.model.document import Document
from frappe.utils import flt

class QualityCheck(Document):
	def validate(self):
		self.calculate_weights()

	def calculate_weights(self):
		accepted = 0
		rejected = 0
		for item in self.items_table:
			item.rejected_qty = flt(item.quantity_kg) - flt(item.accepted_qty)
			accepted += item.accepted_qty
			rejected += item.rejected_qty
		
		self.accepted_weight_kg = accepted
		self.rejected_weight_kg = rejected

	def on_submit(self):
		self.update_procurement_and_submit()

	def update_procurement_and_submit(self):
		if self.procurement:
			proc = frappe.get_doc("Farmer Procurement", self.procurement)
			
			status_map = {
				"Passed": "Passed",
				"Partial Reject": "Partial Reject",
				"Full Reject": "Full Reject"
			}
			# Note: self.overall_result options are "Passed", "Partial Reject", "Full Reject"
			proc.quality_check_status = status_map.get(self.overall_result, self.overall_result)
			proc.linked_quality_check = self.name
			
			# Save status updates first
			proc.save()
			
			# Then formally submit the procurement
			# This will trigger FarmerProcurement.on_submit() which creates Inward and Payment
			proc.submit()
			
			if self.overall_result == "Full Reject":
				# Potential notification logic here
				pass
