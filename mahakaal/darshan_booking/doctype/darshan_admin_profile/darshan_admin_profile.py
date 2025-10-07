# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment
from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request


class DarshanAdminProfile(Document):
	pass




PROFILE_TYPE="Darshan Admin Profile"

@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    
    PROFILE_TYPE = "Darshan Admin Profile"
    
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)
    

@frappe.whitelist()
def get_appointment_list(devoteee_profile_id:str=None,  darshan_type: str=None, workflow_state:str=None,  limit_start=0, limit_page_length=10 ) :
    
    return _get_appointment_list(devoteee_profile_id=devoteee_profile_id,  darshan_type=darshan_type, workflow_state=workflow_state, limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=True )




@frappe.whitelist()
def get_appointment(appointment_id:str ) :

    return _get_appointment(devoteee_profile_id=None , appointment_id=appointment_id)


@frappe.whitelist()
def get_self_profile():

    return frappe.get_doc(profile_id=admin_profile_id, profile_type=PROFILE_TYPE)



@frappe.whitelist()
def apply_workflow_on_appointment(appointment_id:str, action: str):
    
    if not frappe.db.exists('Darshan Appointment', {'name': appointment_id}):
        
        return 'appointment_id ' + appointment_id + ' doesnot exist'
        
    appointment_doc = frappe.get_doc('Darshan Appointment', appointment_id)
      
    apply_workflow(appointment_doc, action)  # must match your workflow Action name
        
    return  {'appointment_id': appointment_id, 'workflow_state': appointment_doc.workflow_state}
