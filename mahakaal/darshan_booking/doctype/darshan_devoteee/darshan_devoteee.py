# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

@frappe.whitelist()   # makes the function callable from frontend
def test_server_action(doc):
    # doc is the current document (Devoteee Profile) passed automatically
    frappe.msgprint(_("this is from Server Action code"))


class DarshanDevoteee(Document):
	pass





