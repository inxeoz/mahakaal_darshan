// Copyright (c) 2025, inx and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Darshan Devoteee", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Darshan Devoteee', {
    refresh: function(frm) {
        if (!frm.custom_buttons || !frm.custom_buttons['Apply Darshan Appointment']) {
            frm.add_custom_button(__('Apply for Darshan Appointment'), () => {
                const defaults = {
                    devoteee_profile: frm.doc.name,
                };
                frappe.new_doc('Darshan Appointment', defaults);
            });
        }
    }
});
