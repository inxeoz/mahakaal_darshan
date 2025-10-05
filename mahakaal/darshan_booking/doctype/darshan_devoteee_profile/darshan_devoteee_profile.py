# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment

from ..active_session.active_session import _is_profile_exist, _login_request


@frappe.whitelist()   # makes the function callable from frontend
def test_server_action(doc):
    # doc is the current document (Devoteee Profile) passed automatically
    frappe.msgprint(_("this is from Server Action code"))


class DarshanDevoteeeProfile(Document):
	pass



PROFILE_TYPE="Darshan Devoteee Profile"


@frappe.whitelist()
def create_devoteee_user(phone:int, name:str):
    
    profile_id = _is_profile_exist(phone=phone, profile_type=PROFILE_TYPE)
    
    if profile_id :
        return {'err' : 'user exist' }
        
    profile = frappe.get_doc({
        'doctype': PROFILE_TYPE,
        'phone': phone,
        'devoteee_name' : name
    })
    
    profile.insert()
    frappe.db.commit()
    
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)
    

@frappe.whitelist()
def update_profile(profile_id: str, info: dict):

    profile = frappe.get_doc(PROFILE_TYPE, profile_id)

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
def create_appointment(profile_id: str, details: dict):
    
    doc = frappe.get_doc({
        "doctype": "Darshan Appointment",
        "devoteee_profile": profile_id,
        **details
    })

    doc.insert()
    frappe.db.commit()

    if not details['save_as_draft']:
        apply_workflow(doc, "Submit")  # must match your workflow Action name
        frappe.db.commit()
        doc.reload()

    return  {"name": doc.name, "workflow_state": doc.workflow_state}



@frappe.whitelist()
def get_appointment_list(profile_id:str, limit_start=0, limit_page_length=10) :
    
    return _get_appointment_list(devoteee_profile_id=profile_id,  limit_start=limit_start, limit_page_length=limit_page_length )



@frappe.whitelist()
def get_appointment(profile_id:str,appointment_id:str ) :
    
    return _get_appointment(devoteee_profile_id=profile_id , appointment_id=appointment_id)


@frappe.whitelist()
def get_profile(profile_id:str):
    
    return {'profile': frappe.get_doc(PROFILE_TYPE, profile_id) }