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

from ..vip_darshan_booking_slot.vip_darshan_booking_slot import update_slot_occupancy

PROFILE_TYPE = "Darshan Approver Profile"
PROFILE_ROLE = "Approver Role"


class DarshanApproverProfile(Document):
    """Document for Darshan Approver profile."""
    pass


def _appointment_exists(appointment_id: str) -> bool:
    return frappe.db.exists("Darshan Appointment", {"name": appointment_id}) is not None


@frappe.whitelist()
@_ensure_role("Administrator")
def create_approver(phone: int) -> Dict[str, Any]:
    return _create_profile(phone=phone, profile_type=PROFILE_TYPE, role_name=PROFILE_ROLE)


@frappe.whitelist(allow_guest=True)
def login_request(phone: int) -> Dict[str, Any]:
    return _login_request(phone=phone, profile_type=PROFILE_TYPE)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_appointment_list(
    devoteee_profile_id: Optional[str] = None,
    darshan_type: Optional[str] = None,
    workflow_state: Optional[str] = None,
    limit_start: int = 0,
    limit_page_length: int = 10,
):
    return _get_appointment_list(
        devoteee_profile_id=devoteee_profile_id,
        darshan_type=darshan_type,
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
    return _get_appointment(devoteee_profile_id=None, appointment_id=appointment_id)


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def get_self_profile():
    current_user = frappe.session.user

    return frappe.get_doc(PROFILE_TYPE, {"frappe_profile": current_user})


def _apply_workflow_on_appointment(appointment_id: str, action: str) -> Dict[str, Any]:

    if not _appointment_exists(appointment_id):
        return {"error": "not_found", "message": f"appointment_id '{appointment_id}' does not exist"}

    # use get_doc to fetch; will raise if problem — that bubble up as exception handled by frappe framework
    appointment_doc = frappe.get_doc("Darshan Appointment", appointment_id)
    
    # apply_workflow mutates appointment_doc
    apply_workflow(appointment_doc, action)

    if action == "Approve" :
        
        darshan_companion_count = len(appointment_doc.darshan_companion)
        
        slot_start_time = appointment_doc.slot_start_time
        slot_end_time = appointment_doc.slot_end_time
        
        
        str_date = appointment_doc.darshan_date.strftime("%Y-%m-%d")
        
        update_slot_occupancy(slot_date=str_date, slot_start_time =slot_start_time, slot_end_time =slot_end_time, number_of_people= darshan_companion_count + 1, slot_name=appointment_doc.slot_name )


    return {"appointment_id": appointment_id, "workflow_state": appointment_doc.workflow_state}


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def approve_appointment(appointment_id: str):
    return _apply_workflow_on_appointment(appointment_id=appointment_id, action="Approve")


@frappe.whitelist()
@_ensure_role(PROFILE_ROLE)
def reject_appointment(appointment_id: str):
    return _apply_workflow_on_appointment(appointment_id=appointment_id, action="Reject")
