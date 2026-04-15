import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Dispatch ID"), "fieldname": "name", "fieldtype": "Link", "options": "Dispatch Order", "width": 140},
        {"label": _("Date"), "fieldname": "dispatch_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle Master", "width": 120},
        {"label": _("Driver Mobile"), "fieldname": "driver_mobile", "fieldtype": "Data", "width": 120},
        {"label": _("Route"), "fieldname": "delivery_route", "fieldtype": "Link", "options": "Delivery Route", "width": 130},
        {"label": _("Total Weight (kg)"), "fieldname": "total_weight_kg", "fieldtype": "Float", "width": 130},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Delivery Note"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 140},
        {"label": _("POD"), "fieldname": "proof_of_delivery", "fieldtype": "Attach", "width": 80},
    ]

def get_data(filters):
    cond = "WHERE docstatus = 1"
    vals = {}
    if filters.get("from_date"):
        cond += " AND dispatch_date >= %(from_date)s"
        vals["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        cond += " AND dispatch_date <= %(to_date)s"
        vals["to_date"] = filters["to_date"]
    if filters.get("customer"):
        cond += " AND customer = %(customer)s"
        vals["customer"] = filters["customer"]
    if filters.get("status"):
        cond += " AND status = %(status)s"
        vals["status"] = filters["status"]

    rows = frappe.db.sql(f"""
        SELECT do.name, do.dispatch_date, do.customer, do.vehicle,
               vm.driver_mobile, do.delivery_route, do.total_weight_kg,
               do.status, do.delivery_note, do.proof_of_delivery
        FROM `tabDispatch Order` do
        LEFT JOIN `tabVehicle Master` vm ON vm.name = do.vehicle
        {cond}
        ORDER BY do.dispatch_date DESC
    """, vals, as_dict=True)
    return rows
