import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("GSTIN"), "fieldname": "billing_address_gstin", "fieldtype": "Data", "width": 140},
        {"label": _("Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("HSN"), "fieldname": "gst_hsn_code", "fieldtype": "Data", "width": 100},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Taxable Amount"), "fieldname": "taxable_value", "fieldtype": "Currency", "width": 140},
        {"label": _("IGST"), "fieldname": "igst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("CGST"), "fieldname": "cgst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("SGST"), "fieldname": "sgst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT si.customer, si.customer_name, si.billing_address_gstin, si.name,
               si.posting_date, sii.gst_hsn_code, SUM(sii.qty) AS qty,
               SUM(sii.taxable_value) AS taxable_value,
               SUM(sii.igst_amount) AS igst_amount,
               SUM(sii.cgst_amount) AS cgst_amount,
               SUM(sii.sgst_amount) AS sgst_amount,
               si.grand_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1
          AND si.company = %(company)s
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY si.name, sii.gst_hsn_code
        ORDER BY si.posting_date
    """, filters, as_dict=True)
