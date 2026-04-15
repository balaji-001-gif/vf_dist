import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Farmer"), "fieldname": "farmer", "fieldtype": "Link", "options": "Farmer", "width": 150},
        {"label": _("Farmer Name"), "fieldname": "farmer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Procurement"), "fieldname": "procurement", "fieldtype": "Link", "options": "Farmer Procurement", "width": 140},
        {"label": _("Date"), "fieldname": "procurement_date", "fieldtype": "Date", "width": 100},
        {"label": _("Due Amount"), "fieldname": "due_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Deductions"), "fieldname": "deductions", "fieldtype": "Currency", "width": 120},
        {"label": _("Net Payable"), "fieldname": "net_payable", "fieldtype": "Currency", "width": 120},
        {"label": _("Paid"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Payment Date"), "fieldname": "payment_date", "fieldtype": "Date", "width": 100},
        {"label": _("UTR"), "fieldname": "utr_number", "fieldtype": "Data", "width": 140},
    ]


def get_data(filters):
    conditions = "WHERE fp.docstatus = 1"
    values = {}

    if filters.get("farmer"):
        conditions += " AND fp.farmer = %(farmer)s"
        values["farmer"] = filters["farmer"]
    if filters.get("from_date"):
        conditions += " AND fp.payment_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND fp.payment_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]
    if filters.get("status"):
        conditions += " AND fp.status = %(status)s"
        values["status"] = filters["status"]

    data = frappe.db.sql(f"""
        SELECT
            fp.farmer,
            f.farmer_name,
            fp.procurement,
            fpr.procurement_date,
            fp.due_amount,
            (fp.due_amount - fp.net_payable) AS deductions,
            fp.net_payable,
            CASE WHEN fp.status = 'Processed' THEN fp.net_payable ELSE 0 END AS paid_amount,
            CASE WHEN fp.status != 'Processed' THEN fp.net_payable ELSE 0 END AS balance,
            fp.status,
            fp.payment_date,
            fp.utr_number
        FROM `tabFarmer Payment` fp
        LEFT JOIN `tabFarmer` f ON f.name = fp.farmer
        LEFT JOIN `tabFarmer Procurement` fpr ON fpr.name = fp.procurement
        {conditions}
        ORDER BY fp.farmer, fpr.procurement_date
    """, values, as_dict=True)

    return data
