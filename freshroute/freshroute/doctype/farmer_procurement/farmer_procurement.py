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

	def after_insert(self):
		"""Automatically create a Draft Quality Check when Procurement is saved."""
		qc = frappe.new_doc("Quality Check")
		qc.procurement = self.name
		qc.qc_date = self.procurement_date
		
		for item in self.items_table:
			qc.append("items_table", {
				"item_code": item.item_code,
				"quantity_kg": item.quantity_kg,
				"accepted_qty": 0,
				"rejected_qty": 0,
				"grading": "A"
			})
		
		qc.insert(ignore_permissions=True)
		frappe.msgprint(f"Draft Quality Check {qc.name} created. Please have the QC team finish it.")

	def on_submit(self):
		"""On submit (triggered by QC submission), create Inward and Payment."""
		self.create_inward_and_payment()

	def create_inward_and_payment(self):
		# Find the related submitted Quality Check
		qcs = frappe.get_all("Quality Check", 
			filters={"procurement": self.name, "docstatus": 1}, 
			fields=["name"]
		)
		
		if not qcs:
			frappe.throw("No submitted Quality Check found for this Procurement. Submission aborted.")
			
		qc = frappe.get_doc("Quality Check", qcs[0].name)
		
		# 1. Create Cold Storage Inward
		inward = frappe.new_doc("Cold Storage Inward")
		inward.procurement = self.name
		inward.cold_storage = self.cold_storage
		
		accepted_value = 0
		for item in qc.items_table:
			if float(item.accepted_qty) > 0:
				inward.append("items_table", {
					"item_code": item.item_code,
					"quantity_kg": item.accepted_qty,
					"grading": item.grading
				})
				
				# calculate payment due based on procurement rate
				for p_item in self.items_table:
					if p_item.item_code == item.item_code:
						accepted_value += (float(item.accepted_qty) * float(p_item.rate_per_kg))
						break
		
		if len(inward.items_table) > 0:
			inward.insert(ignore_permissions=True)
			inward.submit()
			frappe.msgprint(f"Submitting Inward {inward.name} successfully.")
		
		# 2. Create Farmer Payment
		if accepted_value > 0:
			payment = frappe.new_doc("Farmer Payment")
			payment.farmer = self.farmer
			payment.procurement = self.name
			payment.due_amount = accepted_value
			payment.status = "Pending"
			
			mode = self.payment_mode
			if mode not in ["Bank Transfer", "Cash", "UPI"]:
				mode = "Bank Transfer"
				
			payment.payment_mode = mode
			payment.insert(ignore_permissions=True)
			frappe.msgprint(f"Farmer Payment generated for ₹{accepted_value}.")
