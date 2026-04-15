import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": _("Trips"), "fieldname": "trips", "fieldtype": "Int", "width": 80},
        {"label": _("Total Procured (kg)"), "fieldname": "total_kg", "fieldtype": "Float", "width": 150},
        {"label": _("Total Value (₹)"), "fieldname": "total_value", "fieldtype": "Currency", "width": 140},
        {"label": _("Avg Rate/kg"), "fieldname": "avg_rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Unique Farmers"), "fieldname": "farmers", "fieldtype": "Int", "width": 120},
    ]

def get_data(filters):
    cond = "WHERE docstatus = 1"
    vals = {}
    if filters.get("from_date"):
        cond += " AND procurement_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond += " AND procurement_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]

    return frappe.db.sql(f"""
        SELECT agent,
               COUNT(name) AS trips,
               SUM(total_weight_kg) AS total_kg,
               SUM(total_amount) AS total_value,
               ROUND(SUM(total_amount)/NULLIF(SUM(total_weight_kg),0),2) AS avg_rate,
               COUNT(DISTINCT farmer) AS farmers
        FROM `tabFarmer Procurement`
        {cond}
        GROUP BY agent
        ORDER BY total_value DESC
    """, vals, as_dict=True)
