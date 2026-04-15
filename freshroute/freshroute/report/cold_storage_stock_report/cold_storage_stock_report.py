import frappe
from frappe import _
from frappe.utils import date_diff, today, add_days

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Cold Storage"), "fieldname": "location", "fieldtype": "Link", "options": "Cold Storage Location", "width": 160},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 140},
        {"label": _("Qty (kg)"), "fieldname": "qty_kg", "fieldtype": "Float", "width": 100},
        {"label": _("Inward Date"), "fieldname": "inward_date", "fieldtype": "Date", "width": 110},
        {"label": _("Expiry Date"), "fieldname": "expiry_date", "fieldtype": "Date", "width": 110},
        {"label": _("Age (Days)"), "fieldname": "age_days", "fieldtype": "Int", "width": 100},
        {"label": _("Current Temp (°C)"), "fieldname": "current_temp", "fieldtype": "Float", "width": 130},
        {"label": _("Inward Ref"), "fieldname": "inward_ref", "fieldtype": "Link", "options": "Cold Storage Inward", "width": 140},
    ]

def get_data(filters):
    cond = "WHERE csi.docstatus = 1"
    vals = {}
    if filters.get("cold_storage"):
        cond += " AND csi.cold_storage = %(cold_storage)s"
        vals["cold_storage"] = filters["cold_storage"]
    if filters.get("item_code"):
        cond += " AND ii.item_code = %(item_code)s"
        vals["item_code"] = filters["item_code"]
    if filters.get("show_expiring_only"):
        cond += " AND csi.expiry_date <= %(exp_limit)s"
        vals["exp_limit"] = add_days(today(), 3)

    rows = frappe.db.sql(f"""
        SELECT
            csi.cold_storage AS location,
            ii.item_code,
            ii.item_name,
            ii.quantity_kg AS qty_kg,
            csi.inward_date,
            csi.expiry_date,
            DATEDIFF(CURDATE(), DATE(csi.inward_date)) AS age_days,
            csl.current_temp_c AS current_temp,
            csi.name AS inward_ref
        FROM `tabCold Storage Inward` csi
        JOIN `tabInward Item` ii ON ii.parent = csi.name
        LEFT JOIN `tabCold Storage Location` csl ON csl.name = csi.cold_storage
        {cond}
        ORDER BY csi.cold_storage, csi.expiry_date
    """, vals, as_dict=True)
    return rows
