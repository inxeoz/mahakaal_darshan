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
    
    current_user_id = frappe.session.user
    
    devoteee_profile_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not devoteee_profile_id:
        
        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, devoteee_profile_id) }


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

    # Set difference gives IDs without matching schedules
    no_match_ids = list(all_ids - have_match_ids)

    # Return both if needed, or only no_match_ids based on usage
    return {
        "all_ids": list(all_ids),
        "have_match_ids": list(have_match_ids),
        "no_match_ids": no_match_ids
    }

# delta = timedelta(hours=2, minutes=30)
# time_str = get_time_str(delta)  # Outputs: "02:30:00"

def _assign_attender(appointment_id:str):

    A = frappe.get_doc("Darshan Appointment", appointment_id)

    attenders  = get_attenders(appointment_date=A.darshan_date, slot_start_time=A.slot_start_time, slot_end_time=A.slot_end_time, appointment_type=A.darshan_type)

    A.attender = attenders["no_match_ids"][0]
    
    A.save(ignore_permissions=True)
    
    frappe.db.commit()
    
    # appointment_date: str, start_time: str, end_time: str, appointment_type: str