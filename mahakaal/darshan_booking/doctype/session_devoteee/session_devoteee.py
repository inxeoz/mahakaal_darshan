# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

# correct (relative import)
from ..login import _verify_otp_and_get_token, _generate_otp_and_send, _verify_token
from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment



class SessionDevoteee(Document):
	pass

SESSION_TYPE="Session Devoteee"
PROFILE_TYPE="Darshan Devoteee Profile"


@frappe.whitelist()
def create_user(phone:int):
    
    profile = frappe.db.exists(PROFILE_TYPE, {'phone' : phone})
    if profile is None:
        
        profile = frappe.get_doc({
            'doctype': PROFILE_TYPE,
            'phone': phone
        })
        
        profile.insert()
        frappe.db.commit()
        
    
    return  'user exist'

@frappe.whitelist()
def request_otp(phone:int):
    
    profile = frappe.db.exists(PROFILE_TYPE, {'phone' : phone})
    if profile is None:
        create_user(phone)

    generate_otp_and_send(phone)
    return 'otp sent'
    

def generate_otp_and_send(phone:int):
    return _generate_otp_and_send(phone, session_type=SESSION_TYPE)
    
@frappe.whitelist()
def verify_otp_and_get_token(phone:int, otp:str):
    
    return _verify_otp_and_get_token(phone=phone, otp=otp, session_type=SESSION_TYPE)

@frappe.whitelist()
def verify_token(token:str):
    
    return _verify_token(token, session_type=SESSION_TYPE)



@frappe.whitelist()
def update_profile(token: str, info: dict):
    """
    Create or update a 'Darshan Devoteee' record based on phone.
    Expects at least: {"phone": ...}
    """
    # Verify the token and get the associated user document
    token_doc = _verify_token(token, session_type=SESSION_TYPE)
    if not token_doc:
        return {'err' : 'invalid session token'}

    # Check if profile exists by phone number; if not, create a new profile
    profile_id = frappe.db.exists(PROFILE_TYPE, {'phone': token_doc.phone})
    if profile_id:
        profile = frappe.get_doc(PROFILE_TYPE, profile_id)
    else:
        profile = frappe.new_doc(PROFILE_TYPE)
        profile.phone = token_doc.phone

    # Fields allowed to update
    allowed_fields = ["devoteee_name", "gender", "dob", "email", "aadhar", "address"]

    # Update allowed fields from info dict
    for field in allowed_fields:
        if field in info:
            profile.set(field, info[field])

    # Set is_ekyc_complete flag only once, avoid unnecessary repeated saves
    if profile.aadhar and len(profile.aadhar) > 0:
        profile.is_ekyc_complete = 1

    # Save the profile document
    profile.save()

    # Commit changes in the database
    frappe.db.commit()

    return 'update success'



@frappe.whitelist()
def create_appointment(token: str, details: dict, save_as_draft:bool):
    
        # Verify the token and get the associated user document
    token_doc = _verify_token(token, session_type=SESSION_TYPE)
    if not token_doc:
        return {'err' : 'invalid session token'}

    # Check if profile exists by phone number; if not, create a new profile
    profile_id = frappe.db.exists(PROFILE_TYPE, {'phone': token_doc.phone})
        
    doc = frappe.get_doc({
        "doctype": "Darshan Appointment",
        "devoteee_profile": profile_id,
        **details
    })

    doc.insert()
    frappe.db.commit()
    
        # If not saving as draft, move Draft → Pending via workflow
    if not save_as_draft:
        apply_workflow(doc, "Submit")  # must match your workflow Action name
        frappe.db.commit()
        doc.reload()

    return  {"name": doc.name, "workflow_state": doc.workflow_state}



@frappe.whitelist()
def get_appointment_list(token:str, limit_start=0, limit_page_length=10) :

    token_doc = _verify_token(token, session_type=SESSION_TYPE)
    if not token_doc:
        return {'err' : 'invalid session token'}
    
    return _get_appointment_list(phone=token_doc.phone,  session_type=SESSION_TYPE, limit_start=limit_start, limit_page_length=limit_page_length )

@frappe.whitelist()
def get_appointment(token:str,appointment_id:str ) :

    token_doc = _verify_token(token, session_type=SESSION_TYPE)
    if not token_doc:
        return {'err' : 'invalid session token'}
    
    return _get_appointment(phone=token_doc.phone, appointment_id=appointment_id, session_type=SESSION_TYPE)