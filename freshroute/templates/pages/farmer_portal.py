import frappe

def get_context(context):
    context.no_cache = 1
    
    # Supply default values for variables expected in the template
    # to prevent Jinja DebugUndefined format errors.
    context.farmer_name = frappe.session.user if frappe.session.user != "Guest" else "Guest"
    
    if frappe.session.user != "Guest":
        full_name = frappe.get_value("User", frappe.session.user, "full_name")
        if full_name:
            context.farmer_name = full_name
            
    context.today_weight = 0.0
    context.today_amount = 0.0
    context.pending_payment = 0.0
    context.total_outstanding = 0.0
    context.procurements = []
    context.items = []
    
    return context
