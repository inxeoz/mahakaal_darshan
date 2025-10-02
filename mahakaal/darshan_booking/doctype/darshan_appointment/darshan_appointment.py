
# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class DarshanAppointment(Document):
    pass


ALLOWED_SESSION_TYPES = ["Session Devoteee" , "Session Admin" ]

def get_devoteee_profile_id(phone:int, session_type:str ) :

    is_devotee = session_type == "Session Devoteee" 
    
    if not is_devotee or phone is None:
        return None
    
    devoteee_profile_id = frappe.db.exists("Darshan Devoteee Profile", {'phone': phone})
    
    if  not devoteee_profile_id:
        return None
    return devoteee_profile_id



def _get_appointment_list(phone: int,  session_type:str, limit_start=0, limit_page_length=10):
    
    if not (session_type in ALLOWED_SESSION_TYPES ) :
        return {'err' : 'invalid session token'}
    
    
    devoteee_profile_id = get_devoteee_profile_id(phone=phone, session_type=session_type)
        
    darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for darshan_type in darshan_types:

        darshan_appointments_details[darshan_type] = {}
        for workflow_state in darshan_appointments_states:
            
                filters = {'workflow_state': workflow_state, 'darshan_type' : darshan_type}

            
                if  devoteee_profile_id is not None :
                    filters['devoteee_profile'] = devoteee_profile_id
                
                darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)


        # For multiple fields, supply fields as a list; for all fields, use '*'
        
        filters = {'darshan_type': darshan_type}
        if devoteee_profile_id is not None :
            filters['devoteee_profile'] = devoteee_profile_id
            
        darshan_type_appointments = frappe.get_list(
            'Darshan Appointment',
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            filters = filters,
            fields=[
                'name', 'darshan_date', 'darshan_time', 'darshan_type', 'attender', 'workflow_state'
            ]
        )

        darshan_appointments_details[darshan_type]['Appointment List'] = darshan_type_appointments


    
    return  {'res': darshan_appointments_details }





def _get_appointment( phone:int, appointment_id:str, session_type:str) :
    
    if not (session_type in ALLOWED_SESSION_TYPES )  :
        return {'err' : 'invalid session token'}
    
    devoteee_profile_id = get_devoteee_profile_id(phone=phone, session_type=session_type)

    if devoteee_profile_id:
        
        appointment = frappe.get_doc('Darshan Appointment',  {'name' : appointment_id, 'devoteee_profile' : devoteee_profile_id}  )
        return appointment
    
    appointment = frappe.get_doc('Darshan Appointment', appointment_id)

    return appointment