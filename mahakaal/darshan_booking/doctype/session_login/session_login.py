

# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

import secrets

from frappe.model.document import Document


class SessionLogin(Document):
	pass



def _phone_to_nomail(phone: int) :
    return f"{phone}@nomail.com"

def _create_user(phone:str, role_name: str = None) :
    
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


    if role_name:
        user_doc.append("roles", {
                "doctype": "Has Role",
                "role": role_name
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
    temp_pwd = secrets.token_hex(8)
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


# # @frappe.whitelist()
# # def _is_profile_exist(phone:str, profile_type:str):
    
# #     profile_id = frappe.db.exists(profile_type, {'phone': phone})
# #     return profile_id


# def _get_unique_new_token_for_active_session(token_type:str):
    
#     new_token = secrets.token_hex(16)
    
#     token_exist = frappe.db.exists('Active Session', {token_type: new_token})
#     if token_exist:
#             new_token = secrets.token_hex(16) + secrets.token_hex(2)
#     return new_token

# @frappe.whitelist()
# def login_request(phone:int, profile_type:str):
    
#     profile_id = _is_profile_exist(phone=phone, profile_type=profile_type)

#     if profile_id is None:
#          return {'err' : 'connect ' + profile_type + ' profile not exist '} 
     

#     ### after checks succsess profile exist create token unique and otp    
#     new_session_token = _get_unique_new_token_for_active_session('session_token')
#     new_login_token = _get_unique_new_token_for_active_session('login_token')
#     new_otp = secrets.token_hex(2)
    
        
#     new_session = frappe.get_doc({
#         'doctype': 'Active Session',
  
#         'session_token': new_session_token,
#         'login_token': new_login_token,
  
#         'profile_type' : profile_type,
#         'profile_id' : profile_id,
  
  
#         'phone' : phone,
#         'otp' : new_otp,
#     })
    
#     new_session.insert()
#     frappe.db.commit()
    
#     return  {'login_token': new_login_token}

# @frappe.whitelist()
# def _verify_login_token_and_get_session_token(login_token:str, otp:str):
    
#     active_session_id = frappe.db.exists('Active Session', {'login_token': login_token, 'otp' : otp})
    
#     if active_session_id :
#         active_session = frappe.get_doc('Active Session', active_session_id)
        
#         # active_session.login_token = '' lets not remove it for testing
#         active_session.save()
        
#         return {'session_token' : active_session.session_token}
    
#     return {'err' : 'incorrect credentials'}  # or some status

# @frappe.whitelist()    
# def session_token_to_profile_id(session_token:str):
    
#     active_session_id = frappe.db.exists('Active Session', {'session_token': session_token})
    
#     if active_session_id :
#         active_session = frappe.get_doc('Active Session', active_session_id)
        
        
#         return {'profile_id' : active_session.profile_id, 'profile_type' : active_session.profile_type }
    
#     return {'err' : 'incorrect credentials'}  # or some status
    


