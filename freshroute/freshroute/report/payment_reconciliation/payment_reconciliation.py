import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Party"), "fieldname": "party", "fieldtype": "Data", "width": 160},
        {"label": _("Document"), "fieldname": "document", "fieldtype": "Data", "width": 140},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Invoice/Due Amount"), "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Payment"), "fieldname": "payment_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Outstanding"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 130},
        {"label": _("Mode"), "fieldname": "payment_mode", "fieldtype": "Data", "width": 110},
        {"label": _("UTR/Ref"), "fieldname": "utr_number", "fieldtype": "Data", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    rows = []
    cond = "WHERE docstatus = 1"
    vals = {}
    if filters.get("from_date"):
        cond += " AND payment_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond += " AND payment_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]

    if filters.get("party_type") in ("Farmer", None, ""):
        farmer_rows = frappe.db.sql(f"""
            SELECT farmer AS party, name AS document, payment_date AS date,
                   due_amount AS invoice_amount,
                   CASE WHEN status='Processed' THEN net_payable ELSE 0 END AS payment_amount,
                   CASE WHEN status!='Processed' THEN net_payable ELSE 0 END AS outstanding,
                   payment_mode, utr_number, status
            FROM `tabFarmer Payment` {cond}
            ORDER BY payment_date
        """, vals, as_dict=True)
        rows.extend(farmer_rows)

    return rows
