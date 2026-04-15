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
			self.create_inward_and_payment()

	def create_inward_and_payment(self):
		if not self.procurement:
			return

		proc = frappe.get_doc("Farmer Procurement", self.procurement)
		
		# 1. Create Cold Storage Inward
		inward = frappe.new_doc("Cold Storage Inward")
		inward.procurement = self.procurement
		inward.cold_storage = proc.cold_storage
		
		accepted_value = 0
		for item in self.items_table:
			if float(item.accepted_qty) > 0:
				inward.append("items_table", {
					"item_code": item.item_code,
					"quantity_kg": item.accepted_qty,
					"grading": item.grading
				})
				
				# calculate payment due based on procurement rate
				for p_item in proc.items_table:
					if p_item.item_code == item.item_code:
						accepted_value += (float(item.accepted_qty) * float(p_item.rate_per_kg))
						break
		
		if len(inward.items_table) > 0:
			inward.insert(ignore_permissions=True)
			inward.submit()
		
		# 2. Create Farmer Payment
		if accepted_value > 0:
			payment = frappe.new_doc("Farmer Payment")
			payment.farmer = proc.farmer
			payment.procurement = self.procurement
			payment.due_amount = accepted_value
			payment.status = "Pending"
			
			mode = proc.payment_mode
			if mode not in ["Bank Transfer", "Cash", "UPI"]:
				mode = "Bank Transfer"
				
			payment.payment_mode = mode
			payment.insert(ignore_permissions=True)

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
