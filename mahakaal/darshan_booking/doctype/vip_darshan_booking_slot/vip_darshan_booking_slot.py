# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VipDarshanBookingSlot(Document):
    pass

SLOT_DOC_TYPE = "Vip Darshan Booking Slot"

SLOT_CAPCITY=20

@frappe.whitelist(allow_guest=True)
def get_slot_occupancy_info(slot_date: str):
    
    slot_doc =  _create_slot(slot_date=slot_date)

    return {
            "slot_date": slot_doc.slot_date,
            "slot1_available_occupancy": slot_doc.slot1_available_occupancy,
            "slot2_available_occupancy": slot_doc.slot2_available_occupancy,
            "slot3_available_occupancy": slot_doc.slot3_available_occupancy
        }



def _create_slot(slot_date:str):
    
    slot_id = frappe.db.exists(SLOT_DOC_TYPE, {'slot_date': slot_date})

    if slot_id:
        slot_doc = frappe.get_doc(SLOT_DOC_TYPE, slot_id)
        return slot_doc

    slot_doc = frappe.new_doc({
        "doctype": SLOT_DOC_TYPE,
        "slot_date": slot_date
    })

    slot_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return slot_doc

@frappe.whitelist(allow_guest=True)
def update_slot_occupancy(slot_date: str, number_of_people: int, available_occupancy_name:str):
    
    slot_doc = _create_slot(slot_date=slot_date)

    availble_occupancy = getattr(slot_doc, available_occupancy_name, None)

    if availble_occupancy - number_of_people < 0  :

        return 'Not enough capacity'
        
        
    
    setattr(slot_doc, available_occupancy_name, availble_occupancy - number_of_people)

    slot_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return slot_doc