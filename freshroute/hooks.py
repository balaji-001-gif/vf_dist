app_name = "freshroute"
app_title = "FreshRoute"
app_publisher = "Your Company"
app_description = "Farm to Customer Distribution Platform"
app_email = "admin@freshroute.com"
app_license = "mit"
app_version = "1.0.0"

# Scheduler Events
scheduler_events = {
    "daily": [
        "freshroute.utils.notifications.daily_procurement_alert",
        "freshroute.utils.notifications.expiry_check",
    ],
    "hourly": [
        "freshroute.utils.notifications.cold_storage_temp_check",
    ],
    "cron": {
        "0 6 * * *":  ["freshroute.utils.notifications.update_market_prices"],
        "0 7 * * *":  ["freshroute.utils.notifications.dispatch_reminder"],
        "0 0 * * 0":  ["freshroute.utils.notifications.farmer_payment_due_report"],
        "0 0 1 * *":  ["freshroute.utils.notifications.generate_gst_register"],
    }
}

# Website Route Rules
website_route_rules = [
    {"from_route": "/farmer-portal/<path:name>", "to_route": "farmer_portal"},
    {"from_route": "/customer-portal/<path:name>", "to_route": "customer_portal"},
]

# DocType Events
doc_events = {
    "Quality Check": {
        "on_submit": "freshroute.freshroute.doctype.quality_check.quality_check.on_submit"
    },
    "Farmer Procurement": {
        "on_submit": "freshroute.freshroute.doctype.farmer_procurement.farmer_procurement.on_submit"
    },
    "Dispatch Order": {
        "on_submit": "freshroute.freshroute.doctype.dispatch_order.dispatch_order.on_submit"
    },
    "Cold Storage Inward": {
        "on_submit": "freshroute.freshroute.doctype.cold_storage_inward.cold_storage_inward.on_submit"
    },
    "Cold Storage Outward": {
        "on_submit": "freshroute.freshroute.doctype.cold_storage_outward.cold_storage_outward.on_submit"
    },
}

# Fixtures
fixtures = [
    {"doctype": "Custom Field", "filters": [["module", "=", "FreshRoute"]]},
    {"doctype": "Property Setter", "filters": [["module", "=", "FreshRoute"]]},
]
