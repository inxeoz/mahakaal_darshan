
# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class DarshanAppointment(Document):
    pass


def _create_appointment(info: dict):
    
    darshan_appointment_doc = frappe.get_doc({
        "doctype": "Darshan Appointment",
        **info
    })

    darshan_appointment_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return  darshan_appointment_doc


def _get_appointment( devoteee_profile_id:str, appointment_id:str) :
    
    if devoteee_profile_id:
        
        appointment = frappe.get_doc('Darshan Appointment',  {'name' : appointment_id, 'devoteee_profile' : devoteee_profile_id}  )
        return appointment
    
    appointment = frappe.get_doc('Darshan Appointment', appointment_id)

    return appointment


def _get_appointment_list(devoteee_profile_id: str, appointment_type: str, workflow_state:str, ignore_permissions:bool, limit_start=0, limit_page_length=10 ):
    
    
    filters = { }

    if appointment_type:
        filters['appointment_type'] = appointment_type

    if devoteee_profile_id :
        filters['devoteee_profile'] = devoteee_profile_id


    if workflow_state :
        filters['workflow_state'] = workflow_state

    appointment_type_appointments = frappe.get_list(
        'Darshan Appointment',
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        filters = filters,
        fields=[
            'name', 'appointment_date',  'appointment_type', 'attender', 'workflow_state', "slot_start_time", "slot_end_time"
        ],
        ignore_permissions=ignore_permissions   # <--- bypass permission checks
        
    )
    
    return  appointment_type_appointments




def _get_appointment_stats(devoteee_profile_id: str, ignore_permissions:bool):
    

        
    appointment_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for appointment_type in appointment_types:

        darshan_appointments_details[appointment_type] = {}
        for workflow_state in darshan_appointments_states:
            
                filters = {'workflow_state': workflow_state, 'appointment_type' : appointment_type}

            
                if  devoteee_profile_id :
                    filters['devoteee_profile'] = devoteee_profile_id
                
                darshan_appointments_details[appointment_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)



    
    return   darshan_appointments_details
