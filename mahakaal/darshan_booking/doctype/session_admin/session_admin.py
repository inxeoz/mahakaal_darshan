# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

# correct (relative import)
from ..login import _verify_otp_and_get_token, _generate_otp_and_send


class SessionAdmin(Document):
	pass



SESSION_TYPE="Session Admin"
PROFILE_TYPE="Darshan Admin Profile"

@frappe.whitelist()
def request_otp(phone:int):

    profile = frappe.db.exists(PROFILE_TYPE, {'phone' : phone})
    if profile is None:
        
        ## Admini cant be created using API , need to be created by Administrator
        return {'err' : 'connect to Administrator'}
    
    generate_otp_and_send(phone)
    return {'res' : 'otp sent'}
    

def generate_otp_and_send(phone:int):
    return _generate_otp_and_send(phone, session_type=SESSION_TYPE)
    
@frappe.whitelist()
def verify_otp_and_token(phone:int, otp:str):
    
    return _verify_otp_and_get_token(phone=phone, otp=otp, session_type=SESSION_TYPE)