import frappe
from frappe.utils import today, add_days

def get_context(context):
    context.no_cache = 1
    
    user = frappe.session.user
    if user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
        
    # Check for linked customer
    from freshroute.api.customer_portal import get_linked_customer
    customer = get_linked_customer(user)
    
    context.customer_id = customer
    if not customer:
        context.customer_error = "Your account is not linked to any Customer record. Please contact support to enable ordering."

    # Default delivery date to tomorrow
    context.default_delivery_date = add_days(today(), 1)
        
    try:
        context.items = frappe.get_all(
            "Item", 
            filters={"disabled": 0, "is_sales_item": 1}, 
            fields=["item_code", "item_name", "market_price_per_kg"]
        )
    except Exception:
        context.items = []
        
    return context
