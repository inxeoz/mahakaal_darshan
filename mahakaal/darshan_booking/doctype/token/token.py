# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class token(Document):
    pass



import secrets

@frappe.whitelist()
def generate_otp(phone:int):
    
    token = secrets.token_hex(16)
    otp = secrets.token_hex(2)
    
    existing_token = frappe.db.get_value('token', {'phone' : phone}, ['name'])
    
    result = []
    
    
    if existing_token:
        token_record = frappe.get_doc('token', existing_token)
        token_record.token = token
        token_record.otp = otp
        token_record.save()
    else:
        
        token_record = frappe.get_doc({
            'doctype' : 'token',
            'phone' : phone,
            'token' : token,
            'otp' : otp
        })
        
        token_record.save()
        frappe.db.commit()
    
    #send otp to phone number
    
@frappe.whitelist()
def verify_otp_and_get_token(otp:str, phone:int):
    
    existing_token = frappe.db.get_value('token', {'phone' : phone}, ['name'])
    
    try:
        create_or_update_devoteee_profile(info={"phone": phone})
    except Exception as e:
        print(f"errrrrrrrrrrrrrrrrrrrr{e}")
    
    if existing_token:
        token_record = frappe.get_doc('token', existing_token)
        
        if token_record.otp == otp:
            return token_record.token
    return None


@frappe.whitelist()
def create_or_update_devoteee_profile(token: str, info: dict):
    """
    Create or update a 'Devoteee Profile' record based on phone.
    Expects at least: {"phone": ...}
    """
    devoteee_profile = verify_token_get_profile(token)
    allowed_fields_to_update = ["devoteee_name", "gender", "dob", "email", "aadhar", "address"]

    if devoteee_profile:
        profile = frappe.get_doc("Devoteee Profile", devoteee_profile.name)
    else:
        profile = frappe.get_doc({"doctype": "Devoteee Profile"})

    for field in allowed_fields_to_update:
        if field in info:
            profile.set(field, info[field])


    # print(f"aadhaar ------------------------------->{profile.aadhaar}")
    

    if devoteee_profile:
        profile.save()
    else:
        profile.insert()

    aadhar = frappe.db.get_value("Devoteee Profile", profile.name, "aadhar")

    if len(aadhar) > 0 :
        profile.set('is_ekyc_complete', 1)
        profile.save()


    print(f"aaaaaaaaaaaaaaaaaaaa {aadhar}")
    frappe.db.commit()
    return profile.name


@frappe.whitelist()
def get_profile_details(token:str):
    return verify_token_get_profile(token)

def verify_token_get_profile(token:str):
    
    token_doc = verify_token_get_token_doc(token)
    
    print(f"token token -----------------{token}")
    
    if token_doc is None:
        return None
    else:
        
        doc_name = frappe.db.get_value("Devoteee Profile", {"phone": token_doc.phone})
        
        if doc_name:
            Devoteee_profile = frappe.get_doc("Devoteee Profile", doc_name)
        else:
            Devoteee_profile = None
            
        return Devoteee_profile

def verify_token_get_token_doc(token:str):
    
    token_doc = frappe.db.get_value('token', {'token' : token}, '*')
    
    if token_doc:
        
        print(f"token doc ^^^^^^^^^^^^^^^^^^^^^^^^^^^ {token_doc}")
        return token_doc
    else:
        return None

@frappe.whitelist()
def create_appointment(token: str, details: dict, save_as_draft:bool):
    devoteee_profile = verify_token_get_profile(token)
    if not devoteee_profile:
        return None
    
    doc = frappe.get_doc({
        "doctype": "Darshan Appointment",
        "devoteee_profile": devoteee_profile.name,
        **details
    })

    doc.insert()
    frappe.db.commit()
    
        # If not saving as draft, move Draft → Pending via workflow
    if not save_as_draft:
        apply_workflow(doc, "Submit")  # must match your workflow Action name
        frappe.db.commit()
        doc.reload()

    return {"name": doc.name, "workflow_state": doc.workflow_state}

    
    
@frappe.whitelist()
def get_appointment_list(token: str):
    devoteee_profile = verify_token_get_profile(token)
    if not devoteee_profile:
        return []

    appointments_meta = frappe.get_list(
        'Darshan Appointment',
        filters={'devoteee_profile': devoteee_profile.name},
        fields=['name'],
        order_by='darshan_date desc'
    )

    results = []
    for meta in appointments_meta:
        try:
            doc = frappe.get_doc('Darshan Appointment', meta['name'])
            doc_dict = doc.as_dict()

            # ✅ Only share selected parent fields
            allowed_parent_fields = [
                'name', 'darshan_date', 'darshan_time',
                'darshan_type', 'attender', 'workflow_state'
            ]
            filtered = {k: doc_dict[k] for k in allowed_parent_fields if k in doc_dict}

            # ✅ Only share selected child fields
            filtered['darshan_companion'] = [
                {
                    'name': row.get('companion_name'),
                    'phone': row.get('phone'),
                    'gender': row.get('gender')
                }
                for row in doc_dict.get('darshan_companion', [])
            ]

            results.append(filtered)

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), title=f"get_appointment_list error for {meta.get('name')}")
            continue

    return results



    
@frappe.whitelist()
def get_list_of_appointments_admin(token: str,  limit_start=0, limit_page_length=1):
    
    token_doc = verify_token_get_token_doc(token)
    if token_doc and token_doc.get("user_type") != "admin":
        return {"Error": "user is not admin"}
    
    darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for darshan_type in darshan_types:

        darshan_appointments_details[darshan_type] = {}
        for workflow_state in darshan_appointments_states:
                darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', {'workflow_state': workflow_state, 'darshan_type' : darshan_type})


        # For multiple fields, supply fields as a list; for all fields, use '*'
        darshan_type_appointments = frappe.get_list(
            'Darshan Appointment',
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            filters = {'darshan_type': darshan_type},
            fields=[
                'name', 'darshan_date', 'darshan_time', 'darshan_type', 'attender', 'workflow_state'
            ]
        )

        darshan_appointments_details[darshan_type]['Appointment List'] = darshan_type_appointments


    
    return  darshan_appointments_details


@frappe.whitelist()
def get_appointment_admin_or_user(token:str, appointment_id:str) :

    token_doc = verify_token_get_token_doc(token)
    if token_doc and token_doc.get("user_type") != "admin":
        
        devoteee_profile = verify_token_get_profile(token)
    
        appointment = frappe.get_doc('Darshan Appointment',  {'name' : appointment_id, 'devoteee_profile' : devoteee_profile.name}  )
        return appointment
    
    appointment = frappe.get_doc('Darshan Appointment', appointment_id)

    return appointment