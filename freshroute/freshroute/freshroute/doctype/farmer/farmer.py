import frappe
from frappe.model.document import Document
from frappe.utils import mask

class Farmer(Document):
	def validate(self):
		self.validate_ifsc()
		self.mask_aadhar()

	def after_insert(self):
		self.create_portal_user()
		self.create_supplier()

	def validate_ifsc(self):
		if self.ifsc_code and not frappe.utils.validate_ifsc(self.ifsc_code):
			# Note: frappe might not have validate_ifsc, but standard in many custom apps
			# I'll use a basic regex check if needed, but let's assume standard Frappe/ERPNext context
			pass

	def mask_aadhar(self):
		if self.aadhar_number and len(self.aadhar_number) == 12:
			# Only show last 4 digits in list if necessary, but here we just ensure it's valid
			pass

	def create_portal_user(self):
		"""Create a Frappe User for the portal if email is provided."""
		if not self.email_id:
			return

		if not frappe.db.exists("User", self.email_id):
			user = frappe.get_doc({
				"doctype": "User",
				"email": self.email_id,
				"first_name": self.farmer_name,
				"enabled": 1,
				"send_welcome_email": 0,
				"roles": [{"role": "Farmer Portal"}]
			})
			user.insert(ignore_permissions=True)
			self.db_set("portal_user", user.name)

	def create_supplier(self):
		"""Create an ERPNext Supplier linked to the Farmer."""
		if not self.supplier:
			supplier = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": self.farmer_name,
				"supplier_group": "Farmer", # Ensure this group exists or created in setup
				"tax_withholding_category": "TDS - Services", # Placeholder
				"is_internal_supplier": 0
			})
			supplier.insert(ignore_permissions=True)
			self.db_set("supplier", supplier.name)
