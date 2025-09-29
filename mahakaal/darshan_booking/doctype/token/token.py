# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class token(Document):
    pass



import secrets

@frappe.whitelist(allow_guest=True)
def generate_token(phone:int):
    
    token = secrets.token_hex(2)
    
    existing_token = frappe.db.get_value('token', {'phone' : phone}, ['name'])
    
    
    if existing_token:
        
        token_record = frappe.get_doc('token', existing_token)
        token_record.token = token
        token_record.save()
    else:
        
        token_record = frappe.get_doc({
            'doctype' : 'token',
            'phone' : phone,
            'token' : token
        })
        
        token_record.save()
        frappe.db.commit()