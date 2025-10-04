# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment



class DarshanAdminProfile(Document):
	pass




PROFILE_TYPE="Darshan Admin Profile"

@frappe.whitelist()
def get_appointment_list(limit_start=0, limit_page_length=10) :
    
    return _get_appointment_list( devoteee_profile_id=None, limit_start=limit_start, limit_page_length=limit_page_length )



@frappe.whitelist()
def get_appointment(appointment_id:str ) :
    
    return _get_appointment(devoteee_profile_id=None , appointment_id=appointment_id)


@frappe.whitelist()
def get_profile(profile_id:str):
    
    return frappe.get_doc(profile_id=profile_id, profile_type=PROFILE_TYPE)



@frappe.whitelist()
def apply_workflow_on_appointment(appointment_id:str, action: str):
    
    if not frappe.db.exists('Darshan Appointment', {'name': appointment_id}):
        
        return 'appointment_id ' + appointment_id + ' doesnot exist'
        
    appointment_doc = frappe.get_doc('Darshan Appointment', appointment_id)
      
    apply_workflow(appointment_doc, action)  # must match your workflow Action name
        
    return  {'appointment_id': appointment_id, 'workflow_state': appointment_doc.workflow_state}
