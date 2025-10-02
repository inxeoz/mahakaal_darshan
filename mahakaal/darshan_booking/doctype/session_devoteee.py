# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class session_devoteee(Document):
    pass



import secrets

@frappe.whitelist()
def generate_otp(phone:int):
    
    session_devoteee = secrets.session_devoteee_hex(16)
    otp = secrets.session_devoteee_hex(2)
    
    existing_session_devoteee = frappe.db.get_value('session_devoteee', {'phone' : phone}, ['name'])
    
    result = []
    
    
    if existing_session_devoteee:
        session_devoteee_record = frappe.get_doc('session_devoteee', existing_session_devoteee)
        session_devoteee_record.session_devoteee = session_devoteee
        session_devoteee_record.otp = otp
        session_devoteee_record.save()
    else:
        
        session_devoteee_record = frappe.get_doc({
            'doctype' : 'session_devoteee',
            'phone' : phone,
            'session_devoteee' : session_devoteee,
            'otp' : otp
        })
        
        session_devoteee_record.save()
        frappe.db.commit()
    
    #send otp to phone number
    
@frappe.whitelist()
def verify_otp_and_get_session_devoteee(otp:str, phone:int):
    
    existing_session_devoteee = frappe.db.get_value('session_devoteee', {'phone' : phone}, ['name'])
    
    try:
        create_or_update_devoteee_profile(info={"phone": phone})
    except Exception as e:
        print(f"errrrrrrrrrrrrrrrrrrrr{e}")
    
    if existing_session_devoteee:
        session_devoteee_record = frappe.get_doc('session_devoteee', existing_session_devoteee)
        
        if session_devoteee_record.otp == otp:
            return session_devoteee_record.session_devoteee
    return None


@frappe.whitelist()
def create_or_update_devoteee_profile(session_devoteee: str, info: dict):
    """
    Create or update a 'Darshan Devoteee' record based on phone.
    Expects at least: {"phone": ...}
    """
    devoteee_profile = verify_session_devoteee_get_profile(session_devoteee)
    allowed_fields_to_update = ["devoteee_name", "gender", "dob", "email", "aadhar", "address"]

    if devoteee_profile:
        profile = frappe.get_doc("Darshan Devoteee", devoteee_profile.name)
    else:
        profile = frappe.get_doc({"doctype": "Darshan Devoteee"})

    for field in allowed_fields_to_update:
        if field in info:
            profile.set(field, info[field])


    # print(f"aadhaar ------------------------------->{profile.aadhaar}")
    

    if devoteee_profile:
        profile.save()
    else:
        profile.insert()

    aadhar = frappe.db.get_value("Darshan Devoteee", profile.name, "aadhar")

    if len(aadhar) > 0 :
        profile.set('is_ekyc_complete', 1)
        profile.save()


    print(f"aaaaaaaaaaaaaaaaaaaa {aadhar}")
    frappe.db.commit()
    return profile.name



@frappe.whitelist()
def verify_session_devoteee_get_profile(session_devoteee:str):
    Devoteee_profile,_ = verify_session_devoteee_get_profile_session_devoteee_doc(session_devoteee)
    return Devoteee_profile, 


def verify_session_devoteee_get_profile_session_devoteee_doc(session_devoteee:str):
    
    session_devoteee_doc = frappe.db.get_value('session_devoteee', {'session_devoteee' : session_devoteee}, '*')
    
    print(f"session_devoteee session_devoteee -----------------{session_devoteee}")
    
    if session_devoteee_doc is None:
        return None
    else:
        
        Devoteee_profile = frappe.get_doc("Darshan Devoteee", {"phone": session_devoteee_doc.phone})
                 
        return Devoteee_profile, session_devoteee_doc


@frappe.whitelist()
def create_appointment(session_devoteee: str, details: dict, save_as_draft:bool):
    devoteee_profile = verify_session_devoteee_get_profile(session_devoteee)
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
def get_appointment_list(session_devoteee: str,  limit_start=0, limit_page_length=10):
    
    devoteee_profile, session_devoteee_doc = verify_session_devoteee_get_profile_session_devoteee_doc(session_devoteee)
    
    if session_devoteee_doc is None:
        return None
    # if session_devoteee_doc and session_devoteee_doc.get("user_type") != "admin":
    #     return {"Error": "user is not admin"}
    print(f"user types {session_devoteee_doc.get("user_type")}")
    darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for darshan_type in darshan_types:

        darshan_appointments_details[darshan_type] = {}
        for workflow_state in darshan_appointments_states:
            
                filters = {'workflow_state': workflow_state, 'darshan_type' : darshan_type}

            
                if session_devoteee_doc.get("user_type") != "admin":
                    
                    filters['devoteee_profile'] = devoteee_profile.name
                
                darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)


        # For multiple fields, supply fields as a list; for all fields, use '*'
        
        filters = {'darshan_type': darshan_type}
        if session_devoteee_doc.get("user_type") != "admin":
            
            filters['devoteee_profile'] = devoteee_profile.name
            
        darshan_type_appointments = frappe.get_list(
            'Darshan Appointment',
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            filters = filters,
            fields=[
                'name', 'darshan_date', 'darshan_time', 'darshan_type', 'attender', 'workflow_state'
            ]
        )

        print(f"darshan_type_appointments {darshan_type_appointments}")

        darshan_appointments_details[darshan_type]['Appointment List'] = darshan_type_appointments


    
    return  darshan_appointments_details


@frappe.whitelist()
def get_appointment(session_devoteee:str, appointment_id:str) :

    devoteee_profile, session_devoteee_doc = verify_session_devoteee_get_profile_session_devoteee_doc(session_devoteee)
    if session_devoteee_doc and session_devoteee_doc.get("user_type") != "admin":
    
        appointment = frappe.get_doc('Darshan Appointment',  {'name' : appointment_id, 'devoteee_profile' : devoteee_profile.name}  )
        return appointment
    
    appointment = frappe.get_doc('Darshan Appointment', appointment_id)

    return appointment