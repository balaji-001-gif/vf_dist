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
		self.update_procurement()
		if self.overall_result in ["Pass", "Partial Reject"]:
			# In a real environment, we would trigger:
			# 1. Create Stock Entry (Material Receipt) in ERPNext
			# 2. Create Farmer Payment entry
			pass

	def update_procurement(self):
		if self.procurement:
			proc = frappe.get_doc("Farmer Procurement", self.procurement)
			
			status_map = {
				"Pass": "Passed",
				"Partial Reject": "Partial Reject",
				"Full Reject": "Full Reject"
			}
			proc.quality_check_status = status_map.get(self.overall_result, self.overall_result)
			
			proc.linked_quality_check = self.name
			proc.save()
			
			# If full reject, we might notify the farmer
			if self.overall_result == "Full Reject":
				# self.notify_farmer_rejection()
				pass
