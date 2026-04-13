import frappe
import random

def get_current_market_price(item_code):
	"""
	Mock adapter to fetch the current market price for an item.
	In production, this would call a real Mandi API.
	"""
	base_prices = {
		"Tomato": 30,
		"Potato": 25,
		"Onion": 45,
		"Carrot": 40,
		"Spinach": 15
	}
	
	base = base_prices.get(item_code, 20)
	# Add a random variation of +/- 10%
	variation = base * random.uniform(-0.1, 0.1)
	return round(base + variation, 2)

def update_all_market_prices():
	"""Updates all produce items with fresh mock prices."""
	items = frappe.get_all("Item", filters={"producing_category": ["!=", ""]})
	
	for item in items:
		new_price = get_current_market_price(item.item_code)
		frappe.db.set_value("Item", item.name, "market_price_per_kg", new_price)
	
	frappe.db.commit()
