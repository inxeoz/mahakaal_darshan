# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VipDarshanBookingSlot(Document):
    pass

import datetime

SLOT_DOC_TYPE = "Vip Darshan Booking Slot"

SLOT_CAPCITY=20

@frappe.whitelist(allow_guest=True)
def get_slot_occupancy_info(slot_date: str):
    
    return _create_slot(slot_date=slot_date) 

def _create_slot(slot_date:str):
    
    slot_id = frappe.db.exists(SLOT_DOC_TYPE, {'slot_date': slot_date})

    if slot_id:
        slot_doc = frappe.get_doc(SLOT_DOC_TYPE, slot_id)
    else:
        slot_doc = frappe.get_doc({
            "doctype": SLOT_DOC_TYPE,
            "slot_date": slot_date,
            "slots": [
                {"slot_name": "slot1", "slot_start_time": "12:00:00", "slot_end_time": "12:30:00", "slot_capacity": 20},
                {"slot_name": "slot2", "slot_start_time": "12:30:00", "slot_end_time": "13:00:00", "slot_capacity": 20},
                {"slot_name": "slot3", "slot_start_time": "13:00:00", "slot_end_time": "13:30:00", "slot_capacity": 20},
                {"slot_name": "slot4", "slot_start_time": "13:30:00", "slot_end_time": "14:00:00", "slot_capacity": 20},
            ]
        })
        slot_doc.insert(ignore_permissions=True)
        frappe.db.commit()
      # Return only filtered slot details
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
def update_slot_occupancy(slot_date: str, slot_start_time:datetime.timedelta, slot_end_time:datetime.timedelta, number_of_people: int, slot_name: str):

    # Ensure slot document exists (creates one if missing)
    slot_id = frappe.db.exists(SLOT_DOC_TYPE, {"slot_date": slot_date})
    if slot_id:
        slot_doc = frappe.get_doc(SLOT_DOC_TYPE, slot_id)
    else:
        slot_doc = _create_slot(slot_date)  # this will create and return doc
        slot_doc = frappe.get_doc(SLOT_DOC_TYPE, {"slot_date": slot_date})

    # Find the slot we need to update
    target_slot = next((s for s in slot_doc.slots if s.slot_name == slot_name), None)

    print(f"losts", target_slot)

    if not target_slot:
        return {"error": f"Slot '{slot_name}' not found on {slot_date}"}

    # Check capacity
    if target_slot.slot_capacity - number_of_people < 0:
        return {"error": "Not enough capacity"}

    # Update slot capacity
    target_slot.slot_capacity -= number_of_people

    target_slot.slot_start_time = slot_start_time
    
    target_slot.slot_end_time = slot_end_time
    

    # Save changes
    slot_doc.save(ignore_permissions=True)
    frappe.db.commit()

    # Return updated slot info
    return {
        "message": "Slot occupancy updated successfully",
        "slot_name": target_slot.slot_name,
        "remaining_capacity": target_slot.slot_capacity,
        "slot_date": slot_date,
        "slot_start_time" : slot_start_time,
        "slot_end_time" : slot_end_time
    }
