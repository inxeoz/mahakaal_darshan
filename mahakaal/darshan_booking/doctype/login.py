# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class session_devoteee(Document):
    pass


import secrets

    
ALL_SESSIONS= ["Session Admin", "Session Devoteee", "Session Attender"]
SESSION_TO_PROFILE = {
    "Session Admin" : "Darshan Admin Profile",
    
    "Session Devoteee" : "Darshan Devoteee Profile",
    
    "Session Attender" : "Darshan Attender Profile",
    
}


def _get_unique_token_among_sessions(phone: int):
    token = secrets.token_hex(16)
    for Session in ALL_SESSIONS:
        existing = frappe.db.exists(Session, {'phone': phone})
        if existing:
            token = secrets.token_hex(16) + secrets.token_hex(2)
    return token


def _generate_otp_and_send(phone:int, session_type:str):
    
    profile_id  = _is_profile_exist(phone=phone, session_type=session_type)
    
    if profile_id is None:
         return {'err' : 'connect ' + session_type + ' profile not exist '} 
     

    ### after checks succsess profile exist create token unique and otp    
    token = _get_unique_token_among_sessions(phone)
    otp = secrets.token_hex(2)
    

    ### checking is there previosuly exist token 
    existing = frappe.db.exists(session_type, {'phone': phone})
    
    if existing:
        ### if exist updating old tokens and otp
        doc = frappe.get_doc(session_type, existing)
        doc.token = token
        doc.otp = otp
        doc.profile_id = profile_id
        doc.save()
    else:
        ### if not exist creating new tokens and otp
        
        doc = frappe.get_doc({
            'doctype': session_type,
            'phone': phone,
            'token': token,
            'otp': otp,
            'profile_id' : profile_id
        })
        doc.insert()
    
    frappe.db.commit()
    
    return  'otp sent'
    
def _verify_otp_and_get_token(phone:int, otp:str, session_type:str):
    
    if  not _is_profile_exist(phone=phone, session_type=session_type):
        
         return {'err' : 'connect ' + session_type + ' profile not exist '} 
    
    token_id = frappe.db.exists(session_type, {'phone': phone, 'otp' : otp})
    
    if token_id :
        token_doc = frappe.get_doc(session_type, token_id)
        return token_doc.token
    
    return {'err' : 'incorrect credentials'}  # or some status

    
    #_verify_token

def _is_profile_exist(phone:str, session_type:str):
    
        ### checks profile exist or not
    profile_type = SESSION_TO_PROFILE[session_type]
    
    profile_id = frappe.db.exists(profile_type, {'phone': phone})
    
    print(f"profile id {profile_id}")
    
    if not profile_id :
        
        return None
        # return {'err' : 'connect to administrator , profile doensot exist '}
    return profile_id

def _is_session_token_exist(token:str, session_type:str):
    token_id = frappe.db.exists(session_type, {'token': token})

    if not token_id:
        return None
    
    token_doc = frappe.get_doc(session_type, token_id)
    
    return token_doc
    

    
def _get_profile(token:str, session_type:str):
    
    token_doc = _is_session_token_exist(token=token, session_type=session_type)
    
    if not token_doc  :    
        return {'err' : 'token not exist in session'}

    Devoteee_profile = frappe.get_doc(SESSION_TO_PROFILE[session_type], {"name": token_doc.profile_id} )
                
    return Devoteee_profile