# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from functools import wraps
from typing import Optional, Any, Callable, Dict

from ..darshan_appointment.darshan_appointment import (
    _get_appointment_list,
    _get_appointment,
    _get_appointment_stats,
)
from ..session_login.session_login import (
    _create_profile,
    _login_request,
)

from ..ensure_role import _ensure_role

from ..vip_darshan_slot.vip_darshan_slot import update_slot_occupancy

from ..darshan_attender_profile.darshan_attender_profile import _assign_attender

PROFILE_TYPE = "Darshan Approver Profile"
PROFILE_ROLE = "Approver Role"


class DarshanApproverProfile(Document):
    """Document for Darshan Approver profile."""
    pass



# @_ensure_role("Administrator")
@frappe.whitelist(allow_guest=True)
def create_approver(phone: int) -> Dict[str, Any]:

    return _create_profile(phone=phone, profile_type=PROFILE_TYPE, role_name=PROFILE_ROLE)



@frappe.whitelist(allow_guest=True)
def login_request(phone: int) -> Dict[str, Any]:
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_list(
    devoteee_profile_id: Optional[str] = None,
    appointment_type: Optional[str] = None,
    workflow_state: Optional[str] = None,
    limit_start: int = 0,
    limit_page_length: int = 10,
):
    return _get_appointment_list(
        devoteee_profile_id=devoteee_profile_id,
        appointment_type=appointment_type,
        workflow_state=workflow_state,
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        ignore_permissions=True,
    )


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_stats():
    return _get_appointment_stats(devoteee_profile_id=None, ignore_permissions=True)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment(appointment_id: str):
    return _get_appointment(appointment_id=appointment_id)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_self_profile():

    current_user_id = frappe.session.user

    approver_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not approver_id:

        return {'err' : 'can;t get user not exist'}

    return {'profile': frappe.get_doc(PROFILE_TYPE, approver_id) }




def _apply_workflow_on_appointment(appointment_id: str, action: str) -> Dict[str, Any]:

    # use get_doc to fetch; will raise if problem — that bubble up as exception handled by frappe framework
    appointment_doc = frappe.get_doc("Darshan Appointment", appointment_id)

    # apply_workflow mutates appointment_doc
    apply_workflow(appointment_doc, action)

    if action == "Approve" :
        update_slot_occupancy(appointment_id=appointment_id)


    return {"appointment_id": appointment_id, "workflow_state": appointment_doc.workflow_state}




@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def approve_appointment(appointment_id: str):

     _apply_workflow_on_appointment(appointment_id=appointment_id, action="Approve")
     return _assign_attender(appointment_id=appointment_id)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def reject_appointment(appointment_id: str):
    return _apply_workflow_on_appointment(appointment_id=appointment_id, action="Reject")



@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def update_profile(info: dict):

    current_user_id = frappe.session.user

    approver_id = frappe.db.exists(PROFILE_TYPE, {'frappe_profile' : current_user_id})

    if not approver_id:

        return {'err' : 'can;t update user not exist'}

    approver_doc = frappe.get_doc(PROFILE_TYPE, approver_id)

    # Fields allowed to update
    allowed_fields = ["approver_name", "gender", "dob", "email", "aadhar", "address"]

    # Update allowed fields from info dict
    for field in allowed_fields:
        if field in info:
            approver_doc.set(field, info[field])

    # Set is_ekyc_complete flag only once, avoid unnecessary repeated saves
    if approver_doc.aadhar and len(approver_doc.aadhar) > 0:
        approver_doc.is_ekyc_complete = 1

    # Save the profile document
    approver_doc.save()

    # Commit changes in the database
    frappe.db.commit()

    return 'update success'
