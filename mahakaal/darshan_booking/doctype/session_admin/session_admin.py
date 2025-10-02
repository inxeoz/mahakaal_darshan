# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

# correct (relative import)
from ..login import _verify_otp_and_get_token, _generate_otp_and_send, _verify_token
from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment



class SessionAdmin(Document):
	pass



SESSION_TYPE="Session Admin"
PROFILE_TYPE="Darshan Admin Profile"

@frappe.whitelist()
def request_otp(phone:int):
    
    return _generate_otp_and_send(phone, session_type=SESSION_TYPE)

    
@frappe.whitelist()
def verify_otp_and_get_token(phone:int, otp:str):
    
    return _verify_otp_and_get_token(phone=phone, otp=otp, session_type=SESSION_TYPE)



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


    