# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment,_get_appointment_stats
from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request, _create_profile


class DarshanApproverProfile(Document):
	pass




PROFILE_TYPE="Darshan Approver Profile"


@frappe.whitelist()
def create_approver(phone:int):
    
   return _create_profile(phone=phone, profile_type=PROFILE_TYPE, role_name='Approver Role')
    



@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist()
def get_appointment_list(devoteee_profile_id:str=None,  darshan_type: str=None, workflow_state:str=None,  limit_start=0, limit_page_length=10 ) :
    
    return _get_appointment_list(devoteee_profile_id=devoteee_profile_id,  darshan_type=darshan_type, workflow_state=workflow_state, limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=True )




@frappe.whitelist()
def get_appointment_stats( ):
    return _get_appointment_stats(devoteee_profile_id=None, ignore_permissions=True)
    


@frappe.whitelist()
def get_appointment(appointment_id:str ) :

    return _get_appointment(devoteee_profile_id=None , appointment_id=appointment_id)


@frappe.whitelist()
def get_self_profile():
    current_user_id = frappe.session.user
    return frappe.get_doc(PROFILE_TYPE, {'frappe_profile' : current_user_id})



@frappe.whitelist()
def apply_workflow_on_appointment(appointment_id:str, action: str):
    
    if not frappe.db.exists('Darshan Appointment', {'name': appointment_id}):
        
        return 'appointment_id ' + appointment_id + ' doesnot exist'
        
    appointment_doc = frappe.get_doc('Darshan Appointment', appointment_id)
      
    apply_workflow(appointment_doc, action)  # must match your workflow Action name
        
    return  {'appointment_id': appointment_id, 'workflow_state': appointment_doc.workflow_state}


@frappe.whitelist()
def approve_appointment(appointment_id:str):
    return apply_workflow_on_appointment(appointment_id=appointment_id, action='Approve')


@frappe.whitelist()
def reject_appointment(appointment_id:str):
    return apply_workflow_on_appointment(appointment_id=appointment_id, action='Reject')
