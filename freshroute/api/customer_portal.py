import frappe
import json

@frappe.whitelist(allow_guest=False)
def create_order(items, delivery_date, delivery_address=None):
	"""
	Creates a Sales Order for a customer.
	`items` should be a JSON list of dicts with item_code and qty.
	"""
	user = frappe.session.user
	customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
	
	if not customer:
		contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
		if contact:
			links = frappe.get_all("Dynamic Link", filters={"parent": contact, "link_doctype": "Customer"}, fields=["link_name"])
			if links:
				customer = links[0].link_name
				
	if not customer:
		frappe.throw("Authenticated user is not linked to a Customer record.")

	so = frappe.new_doc("Sales Order")
	so.customer = customer
	so.delivery_date = delivery_date
	
	if delivery_address:
		so.customer_address = delivery_address

	for item_data in json.loads(items):
		so.append("items", {
			"item_code": item_data["item_code"],
			"qty": item_data["qty"],
			"warehouse": item_data.get("warehouse") # Optional
		})
	
	so.insert()
	so.submit()
	
	return {"order_id": so.name, "status": "Confirmed"}

@frappe.whitelist()
def get_order_status(order_id):
	"""Returns the status and delivery info for a specific order."""
	order = frappe.get_doc("Sales Order", order_id)
	
	# Check if any Delivery Note is created
	delivery_notes = frappe.get_all("Delivery Note", 
		filters={"items.against_sales_order": order_id},
		fields=["name", "status", "posting_date", "posting_time"]
	)

	return {
		"name": order.name,
		"status": order.status,
		"delivery_status": order.delivery_status,
		"delivery_notes": delivery_notes
	}

@frappe.whitelist()
def get_price_list():
	"""Returns the current price list for the customer's produce."""
	# Simplified: return Item market prices
	return frappe.get_all("Item",
		fields=["item_code", "item_name", "market_price_per_kg", "produce_category"],
		filters={"disabled": 0, "is_sales_item": 1}
	)
