import frappe
from frappe.model.document import Document

class FarmerProcurement(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		total_weight = 0
		total_amount = 0
		for item in self.items_table:
			item.amount = item.quantity_kg * item.rate_per_kg
			total_weight += item.quantity_kg
			total_amount += item.amount
		
		self.total_weight_kg = total_weight
		self.total_amount = total_amount

	def on_submit(self):
		"""
		Logic to trigger when the procurement is submitted.
		In a real system, this might notify the QC team.
		"""
		frappe.msgprint(f"Procurement {self.name} submitted successfully. Please perform Quality Check.")
