# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class session_devoteee(Document):
    pass


import secrets

    

def _generate_otp_and_send(phone:int, session_type:str):
    
    token = secrets.token_hex(16)
    otp = secrets.token_hex(2)
    
    existing = frappe.db.exists(session_type, {'phone': phone})
    
    if existing:
        doc = frappe.get_doc(session_type, existing)
        doc.token = token
        doc.otp = otp
        doc.save()
    else:
        doc = frappe.get_doc({
            'doctype': session_type,
            'phone': phone,
            'token': token,
            'otp': otp
        })
        doc.insert()
    
    frappe.db.commit()
    
    # TODO: send OTP via SMS or email securely
    
    return otp  # or some status
    
@frappe.whitelist()
def _verify_otp_and_get_token(phone:int, otp:str, session_type:str):
    
    token_id = frappe.db.exists(session_type, {'phone': phone, 'otp' : otp})
    
    if token_id :
        token_doc = frappe.get_doc(session_type, token_id)
        return token_doc.token
    return {'err' : 'incorrect credentials'}  # or some status