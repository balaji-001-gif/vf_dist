import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "ID", "fieldname": "name", "fieldtype": "Link", "options": "Farmer Procurement", "width": 120},
		{"label": "Date", "fieldname": "procurement_date", "fieldtype": "Date", "width": 100},
		{"label": "Farmer", "fieldname": "farmer", "fieldtype": "Link", "options": "Farmer", "width": 150},
		{"label": "Weight (kg)", "fieldname": "total_weight_kg", "fieldtype": "Float", "width": 100},
		{"label": "Amount (₹)", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
		{"label": "QC Status", "fieldname": "quality_check_status", "fieldtype": "Data", "width": 100},
		{"label": "Agent", "fieldname": "agent", "fieldtype": "Link", "options": "User", "width": 120}
	]

def get_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += f" AND procurement_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" AND procurement_date <= '{filters.get('to_date')}'"
		
	return frappe.db.sql(f"""
		SELECT name, procurement_date, farmer, total_weight_kg, total_amount, quality_check_status, agent
		FROM `tabFarmer Procurement`
		WHERE docstatus = 1 {conditions}
		ORDER BY procurement_date DESC
	""", as_dict=True)
