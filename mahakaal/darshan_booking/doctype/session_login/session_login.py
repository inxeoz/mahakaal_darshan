# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import secrets
import frappe
from frappe.model.document import Document


class SessionLogin(Document):
    pass


@frappe.whitelist()
def get_current_session_info():
    u = frappe.get_doc("User", frappe.session.user)
    return {
        "wh": frappe.session.user,
        "user": frappe.session.user,
        "email": u.email,
        "full_name": u.full_name,
        "mobile_no": u.mobile_no
    }


def _phone_to_nomail(phone):
    return f"{str(phone)}@nomail.com"


def _create_user(phone):
    email = _phone_to_nomail(phone)
    exists = frappe.db.exists("User", {"email": email})

    if exists:
        return frappe.get_doc("User", exists)

    u = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": email,
        "enabled": 1,
        "send_welcome_email": 0,
        "user_type": "System User",
        "mobile_no": phone,
        "phone": phone
    })

    u.insert(ignore_permissions=True)
    frappe.db.commit()

    return u


def _login_request(phone, profile_type):
    email = _phone_to_nomail(phone)

    if not frappe.db.exists(profile_type, {"frappe_profile": email}):
        return {"err": "user not exist"}

    u = frappe.get_doc("User", email)
    # pwd = secrets.token_hex(6)
    pwd = "Mpsedc123"

    u.new_password = pwd
    u.save(ignore_permissions=True)

    frappe.get_doc({
        "doctype": "Session Login",
        "user": email,
        "pwd": pwd
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    return {"res": "login using temp password that is sent to your number"}


def _create_profile(phone, profile_type, role_name):
    email = _phone_to_nomail(phone)
    u = _create_user(phone)

    restricted = {"Devoteee Role", "Approver Role", "Attender Role"} - {role_name}
    user_roles = set(frappe.get_roles(u.name))

    if user_roles & restricted:
        return {"err": f"cant create {profile_type} , user have restricted role"}

    if role_name not in user_roles:
        u.append("roles", {"doctype": "Has Role", "role": role_name})
        u.save(ignore_permissions=True)

    if frappe.db.exists(profile_type, {"frappe_profile": email}):
        return {"err": "User exist"}

    frappe.get_doc({
        "doctype": profile_type,
        "phone": phone,
        "frappe_profile": email
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    _login_request(phone=phone, profile_type=profile_type)

    return {"res": f"{profile_type} user created successfully"}



import frappe



@frappe.whitelist(allow_guest=True)
def get_auth_token(phone):
    user = frappe.db.get_value('User', {'name': f'{phone}@nomail.com', 'enabled': 1}, ['name'], as_dict=True)
    if not user:
        return {"status": 0, "message": "User not found or disabled"}

    user_doc = frappe.get_doc('User', user.name)
    
    key  = frappe.generate_hash(length=15)
    secret  = frappe.generate_hash(length=15)
    

    user_doc.api_key = key
    user_doc.api_secret = secret
    

    user_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": 1,
        "message": "Authentication success",
        "token": f"token {key}:{secret}"
    }
