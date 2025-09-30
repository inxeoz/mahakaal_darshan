# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class token(Document):
    pass



import secrets

@frappe.whitelist()
def generate_otp(phone:int):
    
    token = secrets.token_hex(16)
    otp = secrets.token_hex(2)
    
    existing_token = frappe.db.get_value('token', {'phone' : phone}, ['name'])
    
    result = []
    
    
    if existing_token:
        token_record = frappe.get_doc('token', existing_token)
        token_record.token = token
        token_record.otp = otp
        token_record.save()
    else:
        
        token_record = frappe.get_doc({
            'doctype' : 'token',
            'phone' : phone,
            'token' : token,
            'otp' : otp
        })
        
        token_record.save()
        frappe.db.commit()
    
    #send otp to phone number
    
@frappe.whitelist()
def verify_otp_and_get_token(otp:str, phone:int):
    
    existing_token = frappe.db.get_value('token', {'phone' : phone}, ['name'])
    
    try:
        create_or_update_devoteee_profile(info={"phone": phone})
    except Exception as e:
        print(f"errrrrrrrrrrrrrrrrrrrr{e}")
    
    if existing_token:
        token_record = frappe.get_doc('token', existing_token)
        
        if token_record.otp == otp:
            return token_record.token
    return None



def create_or_update_devoteee_profile(info: dict):
    """
    Create or update a 'Devoteee Profile' record based on phone.
    Expects at least: {"phone": ...}
    """
    
    
    phone = info.get("phone")
    if not phone:
        frappe.throw("Phone number is required")

    existing_name = frappe.db.get_value("Devoteee Profile", {"phone": phone}, "name")

    if existing_name:
        profile = frappe.get_doc("Devoteee Profile", existing_name)
        profile.update(info)
        profile.save()
    else:
        profile = frappe.get_doc({
            "doctype": "Devoteee Profile",
            **info
        })
        profile.insert()

    frappe.db.commit()
    return profile.name


def verify_token_get_phone(token:str):
    
    phone = frappe.db.get_value('token', {'token' : token}, ['name'])
    
    if phone:
        return phone
    else:
        return None

@frappe.whitelist()
def get_profile_details(token:str):
    
    phone = verify_token_get_phone(token)
    
    print(f"token token -----------------{phone}")
    
    if phone is None:
        return None
    else:
        
        doc_name = frappe.db.get_value("Devoteee Profile", {"phone": phone})
        
        if doc_name:
            Devoteee_profile = frappe.get_doc("Devoteee Profile", doc_name)
        else:
            Devoteee_profile = None
            
        return Devoteee_profile