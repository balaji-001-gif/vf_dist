import frappe

@frappe.whitelist()
def get_dashboard_data(farmer_id):
	"""Returns summary data for the farmer dashboard."""
	farmer = frappe.get_doc("Farmer", farmer_id)
	
	today_procurement = frappe.db.sql("""
		SELECT SUM(total_amount) as amount, SUM(total_weight_kg) as weight
		FROM `tabFarmer Procurement`
		WHERE farmer = %s AND procurement_date = CURDATE()
		AND docstatus = 1
	""", farmer_id, as_dict=True)

	pending_payment = frappe.db.sql("""
		SELECT SUM(net_payable) as amount
		FROM `tabFarmer Payment`
		WHERE farmer = %s AND status = 'Pending'
	""", farmer_id, as_dict=True)

	return {
		"today_procurement": today_procurement[0] if today_procurement else {"amount": 0, "weight": 0},
		"pending_payment": pending_payment[0]["amount"] if pending_payment and pending_payment[0]["amount"] else 0,
		"farmer_name": farmer.farmer_name,
		"outstanding": farmer.total_outstanding
	}

@frappe.whitelist()
def get_procurements(farmer_id, limit=20):
	"""Returns list of procurements for the farmer."""
	return frappe.get_all("Farmer Procurement", 
		filters={"farmer": farmer_id},
		fields=["name", "procurement_date", "total_weight_kg", "total_amount", "quality_check_status"],
		order_by="procurement_date desc",
		limit=limit
	)

@frappe.whitelist()
def get_payments(farmer_id, limit=20):
	"""Returns list of payments for the farmer."""
	return frappe.get_all("Farmer Payment",
		filters={"farmer": farmer_id},
		fields=["name", "payment_date", "net_payable", "status", "utr_number"],
		order_by="payment_date desc",
		limit=limit
	)
