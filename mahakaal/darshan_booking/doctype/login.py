# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class session_devoteee(Document):
    pass


import secrets

    
ALL_SESSIONS= ["Session Admin", "Session Devoteee", "Session Attender"]


def _get_unique_token_among_sessions(phone: int):
    token = secrets.token_hex(16)
    for Session in ALL_SESSIONS:
        existing = frappe.db.exists(Session, {'phone': phone})
        if existing:
            existing_token = frappe.db.get_value(Session, existing, 'token') or ''
            token = token + existing_token + secrets.token_hex(2)
    return token


def _generate_otp_and_send(phone:int, session_type:str):
    
    token = _get_unique_token_among_sessions(phone)
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
    
def _verify_otp_and_get_token(phone:int, otp:str, session_type:str):
    
    token_id = frappe.db.exists(session_type, {'phone': phone, 'otp' : otp})
    
    if token_id :
        token_doc = frappe.get_doc(session_type, token_id)
        return token_doc.token
    return {'err' : 'incorrect credentials'}  # or some status



def _verify_token(token:str, session_type:str):
    
    existing = frappe.db.exists(session_type, {'token': token})

    if not existing:
        return None
    
    token_doc = frappe.get_doc(session_type, existing)
    
    return token_doc
    