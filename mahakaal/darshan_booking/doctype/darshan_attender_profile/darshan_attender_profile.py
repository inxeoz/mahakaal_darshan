# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request


class DarshanAttenderProfile(Document):
	pass





PROFILE_TYPE="Darshan Attender Profile"


@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    
    PROFILE_TYPE = "Darshan Attender Profile"
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist()
def get_profile():
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, devoteee_profile_id) }