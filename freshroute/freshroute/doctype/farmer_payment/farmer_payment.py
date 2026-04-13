import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FarmerPayment(Document):
	def validate(self):
		self.calculate_net_payable()

	def calculate_net_payable(self):
		total_deductions = sum([flt(d.amount) for d in self.deductions_table])
		self.net_payable = flt(self.due_amount) - total_deductions

	def on_submit(self):
		"""
		Logic to update farmer's outstanding balance.
		In a real system, this would also create a Payment Entry in ERPNext.
		"""
		if self.farmer:
			farmer = frappe.get_doc("Farmer", self.farmer)
			# Re-calculate total outstanding (simplistic approach for mock)
			farmer.total_outstanding = flt(farmer.total_outstanding) - flt(self.net_payable)
			farmer.save()
		
		# Trigger notification
		# frappe.enqueue("freshroute.utils.notifications.send_payment_notification", doc=self)
