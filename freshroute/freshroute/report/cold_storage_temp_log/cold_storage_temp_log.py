import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)

def get_columns():
    return [
        {"label": _("Location"), "fieldname": "location", "fieldtype": "Link", "options": "Cold Storage Location", "width": 180},
        {"label": _("Timestamp"), "fieldname": "timestamp", "fieldtype": "Datetime", "width": 160},
        {"label": _("Temp (°C)"), "fieldname": "temperature_c", "fieldtype": "Float", "width": 110},
        {"label": _("Humidity (%)"), "fieldname": "humidity_pct", "fieldtype": "Float", "width": 120},
        {"label": _("Min Temp"), "fieldname": "min_temp_c", "fieldtype": "Float", "width": 100},
        {"label": _("Max Temp"), "fieldname": "max_temp_c", "fieldtype": "Float", "width": 100},
        {"label": _("Alert"), "fieldname": "alert_flag", "fieldtype": "Data", "width": 80},
    ]

def get_data(filters):
    cond = "WHERE tl.parenttype = 'Dispatch Order'"
    vals = {}
    # For now report reads transit temp logs from Dispatch Order
    rows = frappe.db.sql("""
        SELECT
            do.customer AS location,
            tl.timestamp,
            tl.temperature_c,
            tl.humidity_pct,
            NULL AS min_temp_c,
            NULL AS max_temp_c,
            '' AS alert_flag
        FROM `tabTemp Log` tl
        JOIN `tabDispatch Order` do ON do.name = tl.parent
        WHERE tl.parenttype = 'Dispatch Order'
        ORDER BY tl.timestamp DESC
        LIMIT 500
    """, vals, as_dict=True)

    # Also pull from Cold Storage Location current readings
    cs_rows = frappe.db.sql("""
        SELECT name AS location, NOW() AS timestamp,
               current_temp_c AS temperature_c, humidity_pct,
               min_temp_c, max_temp_c,
               CASE WHEN current_temp_c > max_temp_c OR current_temp_c < min_temp_c
                    THEN '⚠ OUT OF RANGE' ELSE '✓ OK' END AS alert_flag
        FROM `tabCold Storage Location`
        WHERE is_active = 1
    """, as_dict=True)
    rows.extend(cs_rows)
    return rows
