frappe.pages['cold-storage-live'].on_page_load = function(wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Cold Storage — Live View',
        single_column: true
    });
    $(wrapper).find('.layout-main-section').html(frappe.render_template('cold_storage_live'));
    load_cs_data();
    // Refresh every 60 seconds
    setInterval(load_cs_data, 60000);
};

function load_cs_data() {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Cold Storage Location',
            filters: {is_active: 1},
            fields: ['name', 'location_name', 'current_temp_c', 'min_temp_c', 'max_temp_c',
                     'humidity_pct', 'capacity_kg', 'current_stock_kg'],
            limit: 50
        },
        callback: function(r) {
            var html = '';
            (r.message || []).forEach(function(loc) {
                var in_range = loc.current_temp_c >= loc.min_temp_c && loc.current_temp_c <= loc.max_temp_c;
                var cls = in_range ? 'cs-ok' : 'cs-alert';
                var util = loc.capacity_kg ? Math.round(loc.current_stock_kg / loc.capacity_kg * 100) : 0;
                html += `<div class="col-md-4">
                  <div class="cs-chamber-card">
                    <h6>${loc.location_name || loc.name}</h6>
                    <div class="cs-temp ${cls}">${loc.current_temp_c || '--'}°C</div>
                    <div>Humidity: ${loc.humidity_pct || '--'}%</div>
                    <div>Utilisation: ${util}% (${loc.current_stock_kg || 0} / ${loc.capacity_kg || 0} kg)</div>
                    <div>Range: ${loc.min_temp_c}°C – ${loc.max_temp_c}°C</div>
                    <div class="${cls}">${in_range ? '✓ Normal' : '⚠ Out of Range'}</div>
                  </div>
                </div>`;
            });
            $('#cs-cards-container').html(html || '<p class="text-muted">No active cold storage locations found.</p>');
        }
    });
}
