import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"label": _("Supplier Name"), "fieldname": "supplier_name", "fieldtype": "Data", "width": 150},
        {"label": _("GSTIN"), "fieldname": "supplier_gstin", "fieldtype": "Data", "width": 140},
        {"label": _("Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("HSN"), "fieldname": "gst_hsn_code", "fieldtype": "Data", "width": 100},
        {"label": _("Taxable Amount"), "fieldname": "taxable_value", "fieldtype": "Currency", "width": 140},
        {"label": _("IGST"), "fieldname": "igst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("CGST"), "fieldname": "cgst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("SGST"), "fieldname": "sgst_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT pi.supplier, pi.supplier_name, pi.supplier_gstin, pi.name,
               pi.posting_date, pii.gst_hsn_code,
               SUM(pii.taxable_value) AS taxable_value,
               SUM(pii.igst_amount) AS igst_amount,
               SUM(pii.cgst_amount) AS cgst_amount,
               SUM(pii.sgst_amount) AS sgst_amount,
               pi.grand_total
        FROM `tabPurchase Invoice` pi
        JOIN `tabPurchase Invoice Item` pii ON pii.parent = pi.name
        WHERE pi.docstatus = 1
          AND pi.company = %(company)s
          AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY pi.name, pii.gst_hsn_code
        ORDER BY pi.posting_date
    """, filters, as_dict=True)
