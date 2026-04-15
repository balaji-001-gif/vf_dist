frappe.pages['freshroute-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'FreshRoute Dashboard',
        single_column: true
    });

    $(wrapper).find('.layout-main-section').html(frappe.render_template('freshroute_dashboard'));
    freshroute_dashboard.load_stats();
};

var freshroute_dashboard = {
    load_stats: function() {
        // Today's procurement
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Farmer Procurement',
                filters: [
                    ['procurement_date', '=', frappe.datetime.get_today()],
                    ['docstatus', '=', 1]
                ],
                fields: ['total_weight_kg', 'total_amount'],
                limit: 500
            },
            callback: function(r) {
                var kg = 0, amt = 0;
                (r.message || []).forEach(function(d) {
                    kg += (d.total_weight_kg || 0);
                    amt += (d.total_amount || 0);
                });
                $('#today-procurement-kg').text(frappe.format(kg, {fieldtype:'Float'}) + ' kg');
                $('#today-procurement-amt').text('₹' + frappe.format(amt, {fieldtype:'Currency'}));
            }
        });

        // Pending farmer payments
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Farmer Payment',
                filters: {status: 'Pending', docstatus: 1},
                fieldname: 'net_payable'
            },
            callback: function(r) {
                var amt = r.message && r.message.net_payable ? r.message.net_payable : 0;
                $('#pending-farmer-payments').text('₹' + frappe.format(amt, {fieldtype:'Currency'}));
            }
        });
    }
};
