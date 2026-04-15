import frappe

def get_context(context):
    context.no_cache = 1
    
    context.items = []
    context.orders = []
    
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
        
    # 1. Market Prices
    try:
        context.items = frappe.get_all("Item", filters={"disabled": 0}, fields=["item_name", "market_price_per_kg"])
    except Exception:
        context.items = []
        
    # 2. Fetch linked Customer
    customer_name = None
    customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
    if customer:
        customer_name = customer
    else:
        contact = frappe.db.get_value("Contact", {"email_id": frappe.session.user}, "name")
        if contact:
            links = frappe.get_all("Dynamic Link", filters={"parent": contact, "link_doctype": "Customer"}, fields=["link_name"])
            if links:
                customer_name = links[0].link_name
                
    # 3. Fetch recent Orders
    if customer_name:
        context.orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer_name, "docstatus": ("<", 2)},
            fields=["name", "delivery_date", "grand_total", "status", "delivery_status"],
            order_by="creation desc",
            limit=10
        )
        
    return context
