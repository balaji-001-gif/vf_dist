import frappe
from frappe.utils import today, add_days

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
        
    # Default delivery date to tomorrow
    context.default_delivery_date = add_days(today(), 1)
        
    try:
        context.items = frappe.get_all(
            "Item", 
            filters={"disabled": 0}, 
            fields=["item_code", "item_name", "market_price_per_kg"]
        )
    except Exception:
        context.items = []
        
    return context
