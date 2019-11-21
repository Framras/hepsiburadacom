// Copyright (c) 2019, Framras AS-Izmir and contributors
// For license information, please see license.txt

frappe.ui.form.on('hepsiburadacom Integration Company Settings', {
	// refresh: function(frm) {

	// }
	check_integration: function(frm){
	    if(frm.doc.username!="")&&(frm.doc.password!="")&&(frm.doc.merchantid!=""){
	        frappe.call({
	            method: "hepsiburadacom.api.check_integration",
	            args:{
	                system: "live",
                    username: frm.doc.username,
                    password: frm.doc.password,
                    merchantid: frm.doc.merchantid
	            },
	            callback: function(r){
                    frm.set_value("result", r.message)
	            }
	        })
	    }
	},
	check_testintegration: function(frm){
	    if(frm.doc.username!="")&&(frm.doc.password!="")&&(frm.doc.merchantid!=""){
	        frappe.call({
	            method: "hepsiburadacom.api.check_integration",
	            args:{
	                system: "test",
                    username: frm.doc.username,
                    password: frm.doc.password,
                    merchantid: frm.doc.merchantid
	            },
	            callback: function(r){
                    frm.set_value("result", r.message)
	            }
	        })
	    }
	}

});
