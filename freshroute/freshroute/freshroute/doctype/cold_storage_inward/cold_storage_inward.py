import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate

class ColdStorageInward(Document):
	def on_submit(self):
		self.create_stock_entry()
		self.update_storage_location()

	def create_stock_entry(self):
		"""
		Create a Material Receipt in ERPNext for the inwarded items.
		"""
		se = frappe.new_doc("Stock Entry")
		se.purpose = "Material Receipt"
		se.stock_entry_type = "Material Receipt"
		
		# Map items to Stock Entry items
		for item in self.items_table:
			se.append("items", {
				"item_code": item.item_code,
				"qty": item.quantity_kg,
				"t_warehouse": frappe.db.get_value("Cold Storage Location", self.cold_storage, "warehouse"),
				"uom": item.uom or frappe.db.get_value("Item", item.item_code, "stock_uom"),
				"basic_rate": 0 # This would usually come from procurement
			})
		
		se.insert()
		se.submit()
		self.db_set("stock_entry", se.name)

	def update_storage_location(self):
		"""Update the current stock in the Cold Storage Location."""
		total_qty = sum([item.quantity_kg for item in self.items_table])
		loc = frappe.get_doc("Cold Storage Location", self.cold_storage)
		loc.current_stock_kg = (loc.current_stock_kg or 0) + total_qty
		loc.save()
		
	def validate(self):
		if not self.expiry_date:
			# Auto-calculate expiry based on item's perishability_days
			perishability = frappe.db.get_value("Item", self.items_table[0].item_code, "perishability_days")
			if perishability:
				self.expiry_date = add_days(getdate(self.inward_date), perishability)
