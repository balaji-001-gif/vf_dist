import frappe
from frappe.model.document import Document

class Farmer(Document):
	def validate(self):
		self.validate_ifsc()
		self.mask_aadhar()

	def after_insert(self):
		self.create_portal_user()
		self.create_supplier()

	def validate_ifsc(self):
		if self.ifsc_code:
			pass

	def mask_aadhar(self):
		if self.aadhar_number and len(self.aadhar_number) == 12:
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
			frappe.db.sql("""
				UPDATE `tabFarmer`
				SET portal_user = %s
				WHERE name = %s
			""", (user.name, self.name))
			frappe.db.commit()

	def create_supplier(self):
		"""Create an ERPNext Supplier linked to the Farmer."""
		if not self.supplier:
			supplier = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": self.farmer_name,
				"supplier_group": "Farmer",
				"tax_withholding_category": "TDS - Services",
				"is_internal_supplier": 0
			})
			supplier.insert(ignore_permissions=True)
			frappe.db.sql("""
				UPDATE `tabFarmer`
				SET supplier = %s
				WHERE name = %s
			""", (supplier.name, self.name))
			frappe.db.commit()
