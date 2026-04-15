import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Procured Qty (kg)"), "fieldname": "procured_qty", "fieldtype": "Float", "width": 140},
        {"label": _("Sold Qty (kg)"), "fieldname": "sold_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Rejected Qty (kg)"), "fieldname": "rejected_qty", "fieldtype": "Float", "width": 130},
        {"label": _("Wastage %"), "fieldname": "wastage_pct", "fieldtype": "Percent", "width": 110},
        {"label": _("Wastage Cost (₹)"), "fieldname": "wastage_cost", "fieldtype": "Currency", "width": 130},
    ]

def get_data(filters):
    cond_proc = "WHERE fp.docstatus = 1"
    vals = {}
    if filters.get("from_date"):
        cond_proc += " AND fp.procurement_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond_proc += " AND fp.procurement_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]
    if filters.get("item_code"):
        cond_proc += " AND pi.item_code = %(item_code)s"
        vals["item_code"] = filters["item_code"]

    procured = frappe.db.sql(f"""
        SELECT pi.item_code, pi.item_name,
               SUM(pi.quantity_kg) AS procured_qty,
               SUM(pi.amount) AS total_cost
        FROM `tabFarmer Procurement` fp
        JOIN `tabProcurement Item` pi ON pi.parent = fp.name
        {cond_proc}
        GROUP BY pi.item_code
    """, vals, as_dict=True)

    sold = {r.item_code: r.qty for r in frappe.db.sql("""
        SELECT sii.item_code, SUM(sii.qty) AS qty
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
        GROUP BY sii.item_code
    """, as_dict=True)}

    rejected = {r.item_code: r.qty for r in frappe.db.sql("""
        SELECT qi.item_code, SUM(qi.rejected_qty) AS qty
        FROM `tabQC Item` qi
        JOIN `tabQuality Check` qc ON qc.name = qi.parent
        WHERE qc.docstatus = 1
        GROUP BY qi.item_code
    """, as_dict=True)}

    results = []
    for row in procured:
        ic = row.item_code
        s = sold.get(ic, 0) or 0
        r = rejected.get(ic, 0) or 0
        p = row.procured_qty or 0
        wastage = p - s - r
        wastage_pct = (wastage / p * 100) if p else 0
        avg_rate = (row.total_cost / p) if p else 0
        results.append({
            "item_code": ic,
            "item_name": row.item_name,
            "procured_qty": p,
            "sold_qty": s,
            "rejected_qty": r,
            "wastage_pct": round(wastage_pct, 2),
            "wastage_cost": round(wastage * avg_rate, 2),
        })
    return results
