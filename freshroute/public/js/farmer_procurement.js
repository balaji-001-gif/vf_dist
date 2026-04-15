// Client script for Farmer Procurement DocType
frappe.ui.form.on('Farmer Procurement', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && !frm.doc.linked_quality_check) {
            frm.add_custom_button(__('Create Quality Check'), function() {
                frappe.model.open_mapped_doc({
                    method: 'freshroute.freshroute.doctype.farmer_procurement.farmer_procurement.make_quality_check',
                    frm: frm
                });
            }, __('Actions'));
        }
    },
    farmer: function(frm) {
        if (frm.doc.farmer) {
            frappe.db.get_value('Farmer', frm.doc.farmer, ['farmer_name', 'agent'], function(r) {
                if (r && r.agent) {
                    frm.set_value('agent', r.agent);
                }
            });
        }
    }
});

frappe.ui.form.on('Procurement Item', {
    item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_value('Item', row.item_code, 'market_price_per_kg', function(r) {
                if (r && r.market_price_per_kg) {
                    frappe.model.set_value(cdt, cdn, 'rate_per_kg', r.market_price_per_kg);
                    frappe.model.set_value(cdt, cdn, 'market_rate_at_time', r.market_price_per_kg);
                    frappe.show_alert({
                        message: __('Rate auto-filled from today\'s mandi price: ₹{0}/kg', [r.market_price_per_kg]),
                        indicator: 'green'
                    });
                }
            });
        }
    },
    rate_per_kg: function(frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
    },
    quantity_kg: function(frm, cdt, cdn) {
        calculate_amount(cdt, cdn);
        calculate_totals(frm);
    },
    items_table_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_amount(cdt, cdn) {
    var row = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, 'amount', (row.quantity_kg || 0) * (row.rate_per_kg || 0));
}

function calculate_totals(frm) {
    var total_kg = 0, total_amt = 0;
    (frm.doc.items_table || []).forEach(function(row) {
        total_kg += (row.quantity_kg || 0);
        total_amt += (row.amount || 0);
    });
    frm.set_value('total_weight_kg', total_kg);
    frm.set_value('total_amount', total_amt);
}
