# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment, _create_appointment, _get_appointment_stats


from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request, _create_profile

from ..ensure_role import _ensure_role


@frappe.whitelist()   # makes the function callable from frontend
def test_server_action(doc):
    # doc is the current document (Devoteee Profile) passed automatically
    frappe.msgprint(_("this is from Server Action code"))


class DarshanDevoteeeProfile(Document):
	pass



PROFILE_TYPE="Darshan Devoteee Profile"
PROFILE_ROLE = "Devoteee Role"



import frappe
import secrets
import traceback

@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)



@frappe.whitelist(allow_guest=True)
def create_devoteee_user(phone:int):
    
   return _create_profile(phone=phone, profile_type=PROFILE_TYPE, role_name='Devoteee Role')
    



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def update_profile(info: dict):
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t update user not exist'}

    devoteee_profile_doc = frappe.get_doc(PROFILE_TYPE, devoteee_profile_id)

    # Fields allowed to update
    allowed_fields = ["devoteee_name", "gender", "dob", "email", "aadhar", "address"]

    # Update allowed fields from info dict
    for field in allowed_fields:
        if field in info:
            devoteee_profile_doc.set(field, info[field])

    # Set is_ekyc_complete flag only once, avoid unnecessary repeated saves
    if devoteee_profile_doc.aadhar and len(profile.aadhar) > 0:
        devoteee_profile_doc.is_ekyc_complete = 1

    # Save the profile document
    devoteee_profile_doc.save()

    # Commit changes in the database
    frappe.db.commit()

    return 'update success'

@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def create_appointment(info: dict):
    
            
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment user not exist'}
    
    return  _create_appointment(devoteee_profile_id=devoteee_profile_id,info=info , ignore_permissions=True)



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_list( darshan_type: str=None, workflow_state:str=None,  limit_start=0, limit_page_length=10 ) :
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment list user not exist'}

    return _get_appointment_list(devoteee_profile_id=devoteee_profile_id,  darshan_type=darshan_type, workflow_state=workflow_state, limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=True )


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_stats( ):

    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment list user not exist'}

    return _get_appointment_stats(devoteee_profile_id=devoteee_profile_id, ignore_permissions=True)
    
    

@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment(appointment_id:str ) :

        
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment user not exist'}
    
    return _get_appointment(devoteee_profile_id=devoteee_profile_id , appointment_id=appointment_id)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_profile():
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, devoteee_profile_id) }


