import frappe
from frappe.utils import now_datetime, getdate, add_days

def send_notification(user, message, mode="Email"):
	"""
	Universal notification sender.
	Can be extended to WhatsApp (Twilio/Gupshup) as requested.
	"""
	if mode == "WhatsApp":
		# Placeholder for Twilio / Gupshup API call
		# print(f"Sending WhatsApp to {user}: {message}")
		pass
	
	# Default to Erappe Email
	frappe.sendmail(
		recipients=[user],
		subject="FreshRoute Notification",
		message=message
	)

def daily_procurement_alert():
	"""Daily alert for scheduled pickups."""
	# Logic to find upcoming procurements and notify Ops
	pass

def expiry_check():
	"""Check for items nearing expiry in cold storage."""
	today = getdate()
	near_expiry = frappe.get_all("Cold Storage Inward", 
		filters={"expiry_date": ["<=", add_days(today, 2)], "docstatus": 1},
		fields=["name", "cold_storage", "expiry_date"]
	)
	
	if near_expiry:
		msg = f"Alert: {len(near_expiry)} batches are expiring within 48 hours."
		# Notify warehouse manager
		pass

def cold_storage_temp_check():
	"""Hourly check of IoT temperature sensors."""
	locations = frappe.get_all("Cold Storage Location", 
		filters={"is_active": 1},
		fields=["name", "current_temp_c", "max_temp_c", "min_temp_c"]
	)
	
	for loc in locations:
		if loc.current_temp_c > loc.max_temp_c or loc.current_temp_c < loc.min_temp_c:
			# Trigger critical alert
			pass

def update_market_prices():
	"""Job to update market prices using the pricing adapter."""
	from freshroute.utils.pricing import update_all_market_prices
	update_all_market_prices()

def dispatch_reminder():
	"""Daily reminder for drivers."""
	pass

def farmer_payment_due_report():
	"""Weekly report of pending payments."""
	pass

def generate_gst_register():
	"""Monthly GST register generation."""
	pass
