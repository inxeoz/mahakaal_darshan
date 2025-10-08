

# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

import secrets

from frappe.model.document import Document


class SessionLogin(Document):
	pass


@frappe.whitelist()
def get_current_session_info():
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



def _phone_to_nomail(phone: int) :
    return f"{phone}@nomail.com"

def _create_user(phone:str) :
    
    nomail = _phone_to_nomail(phone)
    
    user_id = frappe.db.exists('User', {'email' : nomail} )
    
    if user_id:

        user_doc = frappe.get_doc('User', user_id)
        return user_doc

    user_doc = frappe.get_doc({
        "doctype": "User",
        "email": nomail,
        "first_name": nomail,
        "enabled": 1,
        "send_welcome_email": 0,  # Disable welcome email
        "user_type": "System User",
        "mobile_no" : phone,
        "phone" : phone
        
    })

    user_doc.insert(ignore_permissions = True)
    frappe.db.commit()
    
    return user_doc
    

def _login_request(phone: int, profile_type:str):

    nomail = _phone_to_nomail(phone)
    
    profile_id = frappe.db.exists(profile_type, {'frappe_profile': nomail})

    if not profile_id:
        return {'err': 'user not exist'}


 
    user_doc = frappe.get_doc('User', nomail)
    
    # Generate temporary password
    # temp_pwd = secrets.token_hex(8)
    temp_pwd = 'A12345678Hz'
    # user_doc.new_password = temp_pwd
    user_doc.new_password = temp_pwd
    
            # ignore permissions to allow guest-call reset if appropriate; remove if not desired
    user_doc.save(ignore_permissions=True)


    session_login = frappe.get_doc({
        'doctype': 'Session Login',
        'user': nomail,
        'pwd': temp_pwd,
    })
    session_login.insert(ignore_permissions=True)

    frappe.db.commit()

    return {'res': 'login using temp password that is sent to your number'}



def _create_profile(phone:int, profile_type:str, role_name:str):
    
    nomail = _phone_to_nomail(phone)

    user_doc = _create_user(phone)

    roles_set = {"Devoteee Role", "Approver Role", "Attender Role"}
    
    user_roles = set(frappe.get_roles(user_doc.name))  # Convert user roles to set once


    restricted_roles = roles_set - {role_name}  # set difference excludes current role
    if user_roles.intersection(restricted_roles):
        return f"cant create {profile_type} , user have restricted role"

    # Only add the role if user doesn't already have it
    if role_name not in user_roles:
        user_doc.append('roles', {'doctype': 'Has Role', 'role': role_name})
        user_doc.save(ignore_permissions=True)
        frappe.db.commit()


    
    profile_id = frappe.db.exists(profile_type, {'frappe_profile': nomail})
    
    if profile_id:
        return {'err' : 'User exist' }

    profile = frappe.get_doc({
        'doctype': profile_type,
        'phone': phone,
        'frappe_profile' : nomail
    })
    
    profile.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {'res' : profile_type + ' user created successfully'}