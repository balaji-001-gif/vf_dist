import frappe
from frappe.model.document import Document


class DispatchOrder(Document):

    def validate(self):
        self.calculate_total_weight()
        self.validate_vehicle_capacity()

    def calculate_total_weight(self):
        """Sum weight from all dispatch items."""
        total = sum(row.quantity_kg or 0 for row in self.get("items_table"))
        self.total_weight_kg = total

    def validate_vehicle_capacity(self):
        """Warn if total weight exceeds vehicle capacity."""
        if self.vehicle:
            capacity = frappe.db.get_value("Vehicle Master", self.vehicle, "capacity_kg")
            if capacity and self.total_weight_kg > capacity:
                frappe.msgprint(
                    f"Warning: Total weight ({self.total_weight_kg} kg) exceeds "
                    f"vehicle capacity ({capacity} kg) for {self.vehicle}.",
                    alert=True
                )

    def on_submit(self):
        """On submit: create Cold Storage Outward and Delivery Note."""
        self.create_cold_storage_outward()
        self.create_delivery_note()
        self.send_driver_notification()

    def create_cold_storage_outward(self):
        """Auto-create Cold Storage Outward document."""
        if self.cold_storage_outward:
            return  # Already created

        cso = frappe.new_doc("Cold Storage Outward")
        cso.outward_date = frappe.utils.now_datetime()
        cso.dispatch_order = self.name

        # Resolve cold storage source from first item's warehouse if needed
        cold_storage_loc = None
        for item in self.get("items_table"):
            if item.warehouse and not cold_storage_loc:
                cold_storage_loc = frappe.db.get_value("Cold Storage Location", {"warehouse": item.warehouse}, "name")
                
            cso.append("items_table", {
                "item_code": item.item_code,
                "quantity_kg": item.quantity_kg,
                "uom": item.get("uom") or "Kg"
            })

        if not cold_storage_loc:
            frappe.throw("Could not find a valid Cold Storage Location to process outward operations. Please ensure a Source Warehouse is selected on the dispatch items, and that the Warehouse is linked to a Cold Storage Location master.")

        cso.cold_storage = cold_storage_loc
        cso.insert(ignore_permissions=True)
        cso.submit()

        self.db_set("cold_storage_outward", cso.name)
        frappe.msgprint(f"Cold Storage Outward {cso.name} created automatically.")

    def create_delivery_note(self):
        """Auto-create ERPNext Delivery Note from this Dispatch Order."""
        if self.delivery_note:
            return  # Already created

        dn = frappe.new_doc("Delivery Note")
        dn.customer = self.customer
        dn.posting_date = self.dispatch_date

        if self.customer_order:
            dn.against_sales_order = self.customer_order

        for item in self.get("items_table"):
            row_data = {
                "item_code": item.item_code,
                "qty": item.quantity_kg,
                "uom": item.get("uom") or "Kg",
            }
            if self.customer_order:
                row_data["against_sales_order"] = self.customer_order
                so_items = frappe.get_all("Sales Order Item", 
                    filters={"parent": self.customer_order, "item_code": item.item_code}, 
                    fields=["name"]
                )
                if so_items:
                    row_data["so_detail"] = so_items[0].name
                    
            dn.append("items", row_data)

        dn.insert(ignore_permissions=True)
        dn.submit()

        self.db_set("delivery_note", dn.name)
        frappe.msgprint(f"Delivery Note {dn.name} created automatically.")

    def send_driver_notification(self):
        """Send WhatsApp/email notification to driver."""
        from freshroute.utils.notifications import send_notification
        driver_mobile = frappe.db.get_value(
            "Vehicle Master", self.vehicle, "driver_mobile"
        )
        if driver_mobile:
            msg = (
                f"Dispatch Order {self.name} submitted.\n"
                f"Customer: {self.customer}\n"
                f"Date: {self.dispatch_date}\n"
                f"Route: {self.delivery_route or 'N/A'}\n"
                f"Total Weight: {self.total_weight_kg} kg"
            )
            send_notification(driver_mobile, msg, mode="WhatsApp")
