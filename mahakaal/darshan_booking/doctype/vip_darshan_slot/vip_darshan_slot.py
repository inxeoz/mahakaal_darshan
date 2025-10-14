# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VipDarshanSlot(Document):
    pass

import datetime

SLOT_DOC_TYPE = "Vip Darshan Slot"

SLOT_CAPCITY=20


def slot_doc_to_slot_details(slot_doc: Document):

    slot_details = [
        {
            "slot_name": slot.slot_name,
            "slot_start_time": slot.slot_start_time,
            "slot_end_time": slot.slot_end_time,
            "slot_capacity": slot.slot_capacity
        }
        for slot in slot_doc.slots
    ]
    
    return slot_details

@frappe.whitelist(allow_guest=True)
def get_slot_occupancy_info(slot_date: str):

    slot_id = frappe.db.exists(SLOT_DOC_TYPE, {'slot_date': slot_date})

    if not slot_id:
        return _create_slot(slot_date=slot_date) 
    
    slot_doc = frappe.get_doc(SLOT_DOC_TYPE, slot_id)

    return slot_doc_to_slot_details(slot_doc)

def _create_slot(slot_date:str):
    
        
    vip_darshan_slot_info = frappe.get_doc('Booking Slot Info').vip_darshan_slot_info

    slot_doc = frappe.get_doc({
        "doctype": SLOT_DOC_TYPE,
        "slot_date": slot_date,
        "slots": vip_darshan_slot_info
    })

    slot_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return slot_doc_to_slot_details(slot_doc)


@frappe.whitelist(allow_guest=True)
def update_slot_occupancy(appointment_id:str):

    AP= frappe.get_doc("Darshan Appointment", appointment_id) # AP : appointment_doc

    slot_doc = frappe.get_doc(SLOT_DOC_TYPE, {"slot_date": AP.appointment_date.strftime("%Y-%m-%d")})

    # Find the slot we need to update
    TS = next((s for s in slot_doc.slots if s.slot_name == AP.slot_name), None) ## TS : TARGET_SLOT

    # Check capacity
    if TS.slot_capacity - len(AP.darshan_companion) + 1 < 0:
        return {"error": "Not enough capacity"}

    # Update slot capacity
    TS.slot_capacity -= len(AP.darshan_companion) + 1

    TS.slot_start_time = AP.slot_start_time
    
    TS.slot_end_time = AP.slot_end_time
    

    # Save changes
    slot_doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Return updated slot info
    return {
        "message": "Slot occupancy updated successfully",
        "slot_name": TS.slot_name,
        "remaining_capacity": TS.slot_capacity,
        "slot_date": slot_doc.slot_date,
        "slot_start_time" : TS.slot_start_time,
        "slot_end_time" : TS.slot_end_time
    }
