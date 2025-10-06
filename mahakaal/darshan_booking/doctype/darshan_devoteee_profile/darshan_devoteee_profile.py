# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


from ..darshan_appointment.darshan_appointment import  _get_appointment_list, _get_appointment, _create_appointment


from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request


@frappe.whitelist()   # makes the function callable from frontend
def test_server_action(doc):
    # doc is the current document (Devoteee Profile) passed automatically
    frappe.msgprint(_("this is from Server Action code"))


class DarshanDevoteeeProfile(Document):
	pass



PROFILE_TYPE="Darshan Devoteee Profile"


@frappe.whitelist()
def get_current_user_email():
    # get current logged-in user (email/ID)
    current_user = frappe.session.user

    # fetch the User document
    user_doc = frappe.get_doc("User", current_user)

    # return their email field
    return {
        "wh" : current_user,
        "user": current_user,      # usually same as email, e.g. "john@example.com"
        "email": user_doc.email,
        "full_name": user_doc.full_name,
        "mobile_no": user_doc.mobile_no
    }


import frappe
import secrets
import traceback

@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    
    PROFILE_TYPE = "Darshan Devoteee Profile"
    
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist(allow_guest=True)
def create_devoteee_user(phone:int):
    
    nomail = _phone_to_nomail(phone)
    
    profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile': nomail})
    
    if profile_id:
        return 'User exist'

    user_id = frappe.db.exists('User', {'email': nomail})

        
    if user_id:
        return 'user exist'
    
    user_doc = _create_user(phone)
        
    
    profile = frappe.get_doc({
        'doctype': PROFILE_TYPE,
        'phone': phone,
        'frappe_profile' : user_doc.email
    })
    
    profile.insert()
    frappe.db.commit()
    
    return profile
    



@frappe.whitelist()
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
def create_appointment(info: dict):
    
            
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment user not exist'}
    
    return  _create_appointment(devoteee_profile_id=devoteee_profile_id,info=info , ignore_permissions=True)




@frappe.whitelist()
def get_appointment_list( limit_start=0, limit_page_length=10) :
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment list user not exist'}
    
    return _get_appointment_list(devoteee_profile_id=devoteee_profile_id,  limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=True )



@frappe.whitelist()
def get_appointment(appointment_id:str ) :

        
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get appointment user not exist'}
    
    return _get_appointment(devoteee_profile_id=devoteee_profile_id , appointment_id=appointment_id)


@frappe.whitelist()
def get_profile():
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, devoteee_profile_id) }