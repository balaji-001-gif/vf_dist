import frappe
from frappe.utils import today

def get_context(context):
    context.no_cache = 1
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
        
    context.farmer_name = frappe.session.user
    full_name = frappe.get_value("User", frappe.session.user, "full_name")
    if full_name:
        context.farmer_name = full_name
            
    context.today_weight = 0.0
    context.today_amount = 0.0
    context.pending_payment = 0.0
    context.total_outstanding = 0.0
    context.procurements = []
    context.items = []
    
    # 1. Fetch linked Farmer
    farmers = frappe.get_all("Farmer", filters={"portal_user": frappe.session.user}, fields=["name", "farmer_name", "total_outstanding"])
    
    if farmers:
        farmer = farmers[0]
        context.farmer_name = farmer.farmer_name or context.farmer_name
        context.total_outstanding = farmer.total_outstanding or 0.0
        
        # 2. Today's Procurement Stats
        today_date = today()
        today_docs = frappe.get_all(
            "Farmer Procurement",
            filters={"farmer": farmer.name, "procurement_date": today_date, "docstatus": ("<", 2)},
            fields=["total_weight_kg", "total_amount"]
        )
        context.today_weight = sum(d.total_weight_kg or 0 for d in today_docs)
        context.today_amount = sum(d.total_amount or 0 for d in today_docs)
            
        # 3. Pending Payment (sum)
        pending_docs = frappe.get_all(
            "Farmer Payment",
            filters={"farmer": farmer.name, "status": "Pending", "docstatus": ("<", 2)},
            fields=["due_amount"]
        )
        context.pending_payment = sum(d.due_amount or 0 for d in pending_docs)
            
        # 4. Recent procurements list
        context.procurements = frappe.get_all(
            "Farmer Procurement",
            filters={"farmer": farmer.name, "docstatus": ("<", 2)},
            fields=["name", "procurement_date", "total_weight_kg", "total_amount", "quality_check_status"],
            order_by="creation desc",
            limit=10
        )
        
    # 5. Market Prices
    try:
        context.items = frappe.get_all("Item", filters={"disabled": 0}, fields=["item_name", "market_price_per_kg"])
    except Exception:
        context.items = []
        
    return context
