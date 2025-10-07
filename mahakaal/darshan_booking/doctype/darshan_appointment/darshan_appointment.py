
# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class DarshanAppointment(Document):
    pass


def _create_appointment(devoteee_profile_id:str, info: dict, ignore_permissions:bool):

    darshan_appointment_doc = frappe.get_doc({
        "doctype": "Darshan Appointment",
        "devoteee_profile": devoteee_profile_id,
        **info
    })

    darshan_appointment_doc.insert(ignore_permissions=ignore_permissions)
    frappe.db.commit()

    return  darshan_appointment_doc

# def _get_appointment_list(devoteee_profile_id: str, ignore_permissions:bool, limit_start=0, limit_page_length=10, ):
    

        
#     darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
#     darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
#     darshan_appointments_details = {}
    

#     for darshan_type in darshan_types:

#         darshan_appointments_details[darshan_type] = {}
#         for workflow_state in darshan_appointments_states:
            
#                 filters = {'workflow_state': workflow_state, 'darshan_type' : darshan_type}

            
#                 if  devoteee_profile_id :
#                     filters['devoteee_profile'] = devoteee_profile_id
                
#                 darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)


#         # For multiple fields, supply fields as a list; for all fields, use '*'
        
#         filters = {'darshan_type': darshan_type}
#         if  devoteee_profile_id:
#             filters['devoteee_profile'] = devoteee_profile_id
            
#         darshan_type_appointments = frappe.get_list(
#             'Darshan Appointment',
#             limit_start=limit_start,
#             limit_page_length=limit_page_length,
#             filters = filters,
#             fields=[
#                 'name', 'darshan_date', 'darshan_time', 'darshan_type', 'attender', 'workflow_state'
#             ],
#             ignore_permissions=ignore_permissions   # <--- bypass permission checks
            
#         )

#         darshan_appointments_details[darshan_type]['Appointment List'] = darshan_type_appointments


    
#     return   darshan_appointments_details





def _get_appointment( devoteee_profile_id:str, appointment_id:str) :
    
    if devoteee_profile_id:
        
        appointment = frappe.get_doc('Darshan Appointment',  {'name' : appointment_id, 'devoteee_profile' : devoteee_profile_id}  )
        return appointment
    
    appointment = frappe.get_doc('Darshan Appointment', appointment_id)

    return appointment


def _get_appointment_list_by_darshan_type(devoteee_profile_id: str, darshan_type: str, workflow_state:str, ignore_permissions:bool, limit_start=0, limit_page_length=10 ):
    
    
    filters = {'darshan_type': darshan_type }

    if devoteee_profile_id :
        filters['devoteee_profile'] = devoteee_profile_id


    if workflow_state :
        filters['workflow_state'] = workflow_state

    darshan_type_appointments = frappe.get_list(
        'Darshan Appointment',
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        filters = filters,
        fields=[
            'name', 'darshan_date', 'darshan_time', 'darshan_type', 'attender', 'workflow_state'
        ],
        ignore_permissions=ignore_permissions   # <--- bypass permission checks
        
    )
    
    return   darshan_type_appointments




def _get_appointment_stats(devoteee_profile_id: str, ignore_permissions:bool, limit_start=0, limit_page_length=10, ):
    

        
    darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for darshan_type in darshan_types:

        darshan_appointments_details[darshan_type] = {}
        for workflow_state in darshan_appointments_states:
            
                filters = {'workflow_state': workflow_state, 'darshan_type' : darshan_type}

            
                if  devoteee_profile_id :
                    filters['devoteee_profile'] = devoteee_profile_id
                
                darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)



    
    return   darshan_appointments_details
