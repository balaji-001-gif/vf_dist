import frappe
from frappe import _

# ─────────────────────────────────────────────
#  Swiggy / Zomato / Hyperpure REST Adapter
#  Auth: API Key + Secret (Frappe built-in)
#  Rate limit: 1000 req/hr per customer
# ─────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def create_order(customer, items, delivery_date, delivery_address=None):
    """Create Sales Order via REST API (for Swiggy/Zomato/Hyperpure)."""
    import json
    from freshroute.utils.pricing import get_current_market_price

    if isinstance(items, str):
        items = json.loads(items)

    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.delivery_date = delivery_date
    if delivery_address:
        so.customer_address = delivery_address

    for item in items:
        rate = get_current_market_price(item["item_code"])
        so.append("items", {
            "item_code": item["item_code"],
            "qty": item["qty"],
            "rate": rate,
            "uom": item.get("uom", "Kg"),
        })

    so.flags.ignore_permissions = False
    so.insert()
    so.submit()
    return {"order_id": so.name, "status": "Confirmed", "customer": customer}


@frappe.whitelist(allow_guest=False)
def get_order_status(order_id):
    """Get current order status and linked delivery info."""
    order = frappe.get_doc("Sales Order", order_id)
    delivery_notes = frappe.get_all(
        "Delivery Note",
        filters={"items.against_sales_order": order_id},
        fields=["name", "status", "posting_date"]
    )
    dispatch = frappe.get_all(
        "Dispatch Order",
        filters={"customer_order": order_id, "docstatus": 1},
        fields=["name", "status", "actual_delivery_time", "vehicle"]
    )
    return {
        "order_id": order.name,
        "status": order.status,
        "delivery_status": order.delivery_status,
        "delivery_notes": delivery_notes,
        "dispatch": dispatch,
    }


@frappe.whitelist(allow_guest=False)
def get_price_list(customer=None):
    """Return current price list. Customer-specific if provided."""
    items = frappe.get_all(
        "Item",
        filters={"disabled": 0, "is_sales_item": 1},
        fields=["item_code", "item_name", "market_price_per_kg",
                "produce_category", "perishability_days", "grading_standards"]
    )
    return {"items": items, "currency": "INR", "as_of": frappe.utils.now()}


@frappe.whitelist(allow_guest=False)
def get_available_stock(item_code=None):
    """Return available stock in cold storage warehouses."""
    filters = {"actual_qty": [">", 0]}
    fields = ["warehouse", "item_code", "actual_qty", "reserved_qty",
              "projected_qty", "valuation_rate"]
    if item_code:
        filters["item_code"] = item_code

    bins = frappe.get_all("Bin", filters=filters, fields=fields)
    return {"stock": bins, "as_of": frappe.utils.now()}


@frappe.whitelist(allow_guest=False)
def cancel_order(order_id, reason=None):
    """Cancel an existing Sales Order."""
    order = frappe.get_doc("Sales Order", order_id)

    if order.docstatus != 1:
        frappe.throw(_("Only submitted orders can be cancelled."))
    if order.delivery_status in ("Fully Delivered", "Partly Delivered"):
        frappe.throw(_("Cannot cancel a partially or fully delivered order."))

    order.cancel()
    frappe.db.commit()

    return {
        "order_id": order_id,
        "status": "Cancelled",
        "reason": reason or "Cancelled via API"
    }
