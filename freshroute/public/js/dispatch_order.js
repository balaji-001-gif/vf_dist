// Client script for Dispatch Order DocType
frappe.ui.form.on('Dispatch Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) {
            // Vehicle capacity indicator
            if (frm.doc.vehicle && frm.doc.total_weight_kg) {
                frappe.db.get_value('Vehicle Master', frm.doc.vehicle, 'capacity_kg', function(r) {
                    if (r && r.capacity_kg) {
                        var pct = Math.round(frm.doc.total_weight_kg / r.capacity_kg * 100);
                        var color = pct > 100 ? 'red' : pct > 85 ? 'orange' : 'green';
                        frm.dashboard.add_comment(
                            __('Vehicle load: {0} kg / {1} kg ({2}%)', [frm.doc.total_weight_kg, r.capacity_kg, pct]),
                            color, true
                        );
                    }
                });
            }
        }
        if (frm.doc.docstatus === 1) {
            if (!frm.doc.proof_of_delivery) {
                frm.add_custom_button(__('Mark Delivered'), function() {
                    frm.set_value('status', 'Delivered');
                    frm.set_value('actual_delivery_time', frappe.datetime.now_datetime());
                    frm.save();
                }, __('Actions'));
            }
        }
    },
    vehicle: function(frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value('Vehicle Master', frm.doc.vehicle, ['capacity_kg', 'driver_name', 'status'], function(r) {
                if (r) {
                    if (r.status === 'Maintenance') {
                        frappe.show_alert({message: __('Warning: Vehicle is under Maintenance!'), indicator: 'red'});
                    }
                    if (r.status === 'On Route') {
                        frappe.show_alert({message: __('Warning: Vehicle is already On Route!'), indicator: 'orange'});
                    }
                }
            });
        }
    },
    delivery_route: function(frm) {
        if (frm.doc.delivery_route) {
            frappe.db.get_value('Delivery Route', frm.doc.delivery_route, 'assigned_vehicle', function(r) {
                if (r && r.assigned_vehicle && !frm.doc.vehicle) {
                    frm.set_value('vehicle', r.assigned_vehicle);
                    frappe.show_alert({message: __('Vehicle auto-filled from route default'), indicator: 'green'});
                }
            });
        }
    }
});

frappe.ui.form.on('Dispatch Item', {
    quantity_kg: function(frm, cdt, cdn) {
        calculate_dispatch_totals(frm);
    },
    dispatch_items_remove: function(frm) {
        calculate_dispatch_totals(frm);
    }
});

function calculate_dispatch_totals(frm) {
    var total = 0;
    (frm.doc.items_table || []).forEach(function(r) { total += (r.quantity_kg || 0); });
    frm.set_value('total_weight_kg', total);
}
