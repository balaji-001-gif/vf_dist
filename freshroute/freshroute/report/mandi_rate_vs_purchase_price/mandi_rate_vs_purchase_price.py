import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "procurement_date", "fieldtype": "Date", "width": 100},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Mandi Rate (₹/kg)"), "fieldname": "market_rate", "fieldtype": "Currency", "width": 140},
        {"label": _("Procured Rate (₹/kg)"), "fieldname": "procured_rate", "fieldtype": "Currency", "width": 150},
        {"label": _("Variance (₹/kg)"), "fieldname": "variance", "fieldtype": "Currency", "width": 130},
        {"label": _("Variance %"), "fieldname": "variance_pct", "fieldtype": "Percent", "width": 120},
        {"label": _("Qty (kg)"), "fieldname": "qty_kg", "fieldtype": "Float", "width": 100},
    ]

def get_data(filters):
    cond = "WHERE fp.docstatus = 1"
    vals = {}
    if filters.get("from_date"):
        cond += " AND fp.procurement_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond += " AND fp.procurement_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]
    if filters.get("item_code"):
        cond += " AND pi.item_code = %(item_code)s"
        vals["item_code"] = filters["item_code"]

    rows = frappe.db.sql(f"""
        SELECT fp.procurement_date,
               pi.item_code, pi.item_name,
               pi.market_rate_at_time AS market_rate,
               pi.rate_per_kg AS procured_rate,
               (pi.rate_per_kg - pi.market_rate_at_time) AS variance,
               ROUND((pi.rate_per_kg - pi.market_rate_at_time)/NULLIF(pi.market_rate_at_time,0)*100, 2) AS variance_pct,
               pi.quantity_kg AS qty_kg
        FROM `tabFarmer Procurement` fp
        JOIN `tabProcurement Item` pi ON pi.parent = fp.name
        {cond}
        ORDER BY fp.procurement_date DESC
    """, vals, as_dict=True)
    return rows
