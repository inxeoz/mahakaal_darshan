# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt


# import frappe
import frappe

# import frappe
from frappe.model.document import Document

from ..session_login.session_login import _phone_to_nomail, _create_user, _login_request, _create_profile
from ..ensure_role import _ensure_role
from frappe.utils import get_time_str
from datetime import timedelta
from datetime import date
import datetime

class DarshanAttenderProfile(Document):
	pass





PROFILE_TYPE="Darshan Attender Profile"
PROFILE_ROLE = "Attender Role"
DARSHAN_APPOINTMENT = "Darshan Appointment"

# @_ensure_role("Administrator")
@frappe.whitelist(allow_guest=True)
def create_attender(phone:int):
    return _create_profile(phone=phone, profile_type=PROFILE_TYPE, role_name=PROFILE_ROLE)


@frappe.whitelist(allow_guest=True)
def login_request(phone: int):
    
    PROFILE_TYPE = "Darshan Attender Profile"
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist()
def get_profile():
    
    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : frappe.session.user})


    if not attender_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, attender_profile_id) }


@frappe.whitelist()
def get_attenders(appointment_date: datetime.date, slot_start_time: timedelta, slot_end_time: timedelta, appointment_type: str):
    # Fetch all parent IDs once
    all_ids = set(frappe.get_all('Darshan Attender Profile', pluck='name'))

    slot_start_time_str = get_time_str(slot_start_time)
    slot_end_time_str = get_time_str(slot_end_time)
    appointment_date_str = appointment_date.strftime('%Y-%m-%d') 

    # Fetch matching schedule parents
    have_match_ids = set(
        s['parent'] for s in frappe.get_all(
            'Attender Schedule Table',
            filters={
                'appointment_date': appointment_date_str,
                'slot_start_time': slot_start_time_str,
                'slot_end_time': slot_end_time_str,
                'appointment_type': appointment_type
            },
            fields=['parent']
        )
    )

    # Return both if needed, or only no_match_ids based on usage
    return {
        "all_ids": list(all_ids),
        "have_match_ids": list(have_match_ids),
        "no_match_ids": list(all_ids - have_match_ids)
    }

# delta = timedelta(hours=2, minutes=30)
# time_str = get_time_str(delta)  # Outputs: "02:30:00"

def _assign_attender(appointment_id:str):

    A = frappe.get_doc("Darshan Appointment", appointment_id)

    attenders  = get_attenders(appointment_date=A.appointment_date, slot_start_time=A.slot_start_time, slot_end_time=A.slot_end_time, appointment_type=A.appointment_type)

    if attenders["no_match_ids"] :
        attender_id  = attenders["no_match_ids"][0]
    else:
        attender_id  = attenders["all_ids"][0]
    
    # attender_id  = 'ATD000006'
    

    A.attender = attender_id
    
    A.save(ignore_permissions=True)

    _add_appointment_in_attender_schedule(attender_id=attender_id, appointment_id=appointment_id)
    
    frappe.db.commit()
    
    # appointment_date: str, start_time: str, end_time: str, appointment_type: str


def _add_appointment_in_attender_schedule(attender_id:str,  appointment_id:str):

    appointment_doc = frappe.get_doc("Darshan Appointment", appointment_id)

    attender_profile = frappe.get_doc("Darshan Attender Profile", attender_id)


    attender_profile.append('schedule', {
    'appointment_date': appointment_doc.appointment_date.strftime('%Y-%m-%d') ,
    'appointment_type':appointment_doc.appointment_type,

    'slot_start_time': get_time_str ( appointment_doc.slot_start_time ),
    'slot_end_time': get_time_str ( appointment_doc.slot_end_time ),
    'appointment': appointment_id,
    'group_size' : appointment_doc.group_size,
    'primary_devoteee_name' : appointment_doc.primary_devoteee_name
    
    
    })

    attender_profile.save(ignore_permissions=True)

    frappe.db.commit()
    

@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_self_profile():
    
    current_user_id = frappe.session.user
    
    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not attender_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, attender_profile_id) }

@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_attender_appointments_list(appointment_date:str=None):
    

    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : frappe.session.user})

    if appointment_date is None:
        appointment_date = date.today().strftime("%Y-%m-%d")
    else:
        appointment_date = frappe.utils.getdate(appointment_date)

    attender_doc  = frappe.get_doc(PROFILE_TYPE, attender_profile_id)

    schedules = frappe.get_all(
            'Attender Schedule Table',
            filters={
                'appointment_date': appointment_date,
                "parent" : attender_doc.name
            },
            fields=['appointment_date', 'appointment_type', 'slot_start_time', 'slot_end_time', 'appointment', 'name', "mark_exit", "group_size", "primary_devoteee_name"] 
        )

    return schedules


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_attender_appointment_companion_list(appointment_id: str):

    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile': frappe.session.user})

    appointment_id = frappe.db.exists(DARSHAN_APPOINTMENT, {'name': appointment_id, "attender" : attender_profile_id})
    
    # Fetch attender_doc if needed for permission check or additional filtering (optional)
    attender_doc = frappe.get_doc(PROFILE_TYPE, attender_profile_id)

    # Fetch the single schedule row/document by appointment_id (name)
    companion_list = frappe.get_all(
        'Darshan Companion',
        filters={"parent": appointment_id},
        fields=['companion_name', 'companion_phone', 'companion_gender', 'companion_age']  # fetch all fields
    )


    return companion_list



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_attender_appointment(appointment_id:str):
    
    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : frappe.session.user})
    
    appointment_doc = frappe.get_doc(DARSHAN_APPOINTMENT, {"name": appointment_id, "attender": attender_profile_id})

    return appointment_doc

@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def mark_exit(appointment_id:str):

    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : frappe.session.user})

    attender_doc  = frappe.get_doc(PROFILE_TYPE, attender_profile_id)

    # Find the slot we need to update
    schedule_row = next((s for s in attender_doc.schedule if s.appointment == appointment_id), None) ## TS : TARGET_SLOT

    schedule_row.mark_exit = 1

        # Save changes
    attender_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return schedule_row



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_stats(appointment_date: str | None = None):
    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {"frappe_profile": frappe.session.user})
    if not attender_profile_id:
        frappe.throw("Attender profile not found for the current user.")

    appointment_date_obj = getdate(appointment_date) if appointment_date else date.today()

    filters = {
        "appointment_date": appointment_date_obj,
        "parent": attender_profile_id
    }

    total_schedules = frappe.db.count("Attender Schedule Table", filters)
    marked_exit_schedules = frappe.db.count("Attender Schedule Table", {**filters, "mark_exit": 1})

    return {
        "total_schedules": total_schedules,
        "marked_exit_schedules": marked_exit_schedules
    }



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def update_profile(info: dict):
    
    
    attender_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : frappe.session.user})

    if not attender_profile_id:
        
        return {'err' : 'can;t update user not exist'}

    attender_profile_doc = frappe.get_doc(PROFILE_TYPE, attender_profile_id)

    # Fields allowed to update
    allowed_fields = ["attender_name", "gender", "dob", "email", "aadhar", "address"]

    # Update allowed fields from info dict
    for field in allowed_fields:
        if field in info:
            attender_profile_doc.set(field, info[field])

    # Set is_ekyc_complete flag only once, avoid unnecessary repeated saves
    if attender_profile_doc.aadhar and len(attender_profile_doc.aadhar) > 0:
        attender_profile_doc.is_ekyc_complete = 1

    # Save the profile document
    attender_profile_doc.save()

    # Commit changes in the database
    frappe.db.commit()

    return 'update success'