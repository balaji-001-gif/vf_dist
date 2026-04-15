import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Qty (kg)"), "fieldname": "qty", "fieldtype": "Float", "width": 90},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Payment Status"), "fieldname": "payment_status", "fieldtype": "Data", "width": 120},
    ]

def get_data(filters):
    cond = "WHERE si.docstatus = 1"
    vals = {}
    if filters.get("customer"):
        cond += " AND si.customer = %(customer)s"
        vals["customer"] = filters["customer"]
    if filters.get("from_date"):
        cond += " AND si.posting_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond += " AND si.posting_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]
    if filters.get("payment_status"):
        cond += " AND si.payment_terms_template = %(ps)s"
        vals["ps"] = filters["payment_status"]

    return frappe.db.sql(f"""
        SELECT si.customer, si.customer_name, si.name AS invoice,
               si.posting_date, sii.item_code, sii.qty, sii.rate,
               sii.amount, si.payment_terms_template AS payment_status
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        {cond}
        ORDER BY si.posting_date DESC
    """, vals, as_dict=True)
