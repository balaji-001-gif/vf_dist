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

@frappe.whitelist()
def get_procurement_detail(procurement_id):
    """Returns full detail of a single procurement including QC."""
    proc = frappe.get_doc("Farmer Procurement", procurement_id)
    qc = None
    if proc.linked_quality_check:
        qc = frappe.get_doc("Quality Check", proc.linked_quality_check).as_dict()
    return {"procurement": proc.as_dict(), "quality_check": qc}

@frappe.whitelist()
def get_price_board(farmer_id):
    """Returns today's mandi prices for items this farmer grows."""
    farmer = frappe.get_doc("Farmer", farmer_id)
    item_codes = [d.item_code for d in farmer.get("primary_produce", [])]
    filters = {"disabled": 0}
    if item_codes:
        filters["name"] = ["in", item_codes]
    items = frappe.get_all("Item",
        filters=filters,
        fields=["item_code", "item_name", "market_price_per_kg", "produce_category"]
    )
    return {"items": items, "as_of": frappe.utils.now()}

@frappe.whitelist()
def update_profile(farmer_id, bank_account_number=None, bank_account_name=None,
                   ifsc_code=None, mobile_number=None, alternate_mobile=None):
    """Update farmer's bank account and contact details."""
    farmer = frappe.get_doc("Farmer", farmer_id)
    if bank_account_number:
        farmer.bank_account_number = bank_account_number
    if bank_account_name:
        farmer.bank_account_name = bank_account_name
    if ifsc_code:
        farmer.ifsc_code = ifsc_code
    if mobile_number:
        farmer.mobile_number = mobile_number
    if alternate_mobile:
        farmer.alternate_mobile = alternate_mobile
    farmer.save(ignore_permissions=False)
    return {"status": "updated", "farmer": farmer_id}

@frappe.whitelist()
def create_support_ticket(farmer_id, subject, description):
    """Create a support issue linked to the farmer."""
    issue = frappe.new_doc("Issue")
    issue.subject = subject
    issue.description = description
    issue.raised_by = frappe.session.user
    issue.custom_farmer = farmer_id
    issue.insert(ignore_permissions=True)
    return {"issue_id": issue.name, "status": "Open"}
