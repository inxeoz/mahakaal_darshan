
# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow


class DarshanAppointment(Document):
    pass


def _get_appointment_list(phone: int,  session_type:str, limit_start=0, limit_page_length=10):
    
    allowed_session_types = ["Session Devoteee" , "Session Admin" ]
    
    if not (session_type in allowed_session_types ) :
        return {'err' : 'invalid session token'}
    
    
    is_devotee = session_type == "Session Devoteee"
    
    if is_devotee:
        
                # Check if profile exists by phone number; if not, create a new profile
        profile_id = frappe.db.exists("Darshan Devoteee Profile", {'phone': phone})
        
        if  not profile_id :
            return {'err' : 'Session Type Devotee but no Devoteee profile ?? '}
        
        



    darshan_types = ["Shigra Darshan", "Bhasm Arti", "Vip Darshan", "Localide Darshan"]
    darshan_appointments_states = ["Pending", "Approved", "Rejected", "Cancelled"]
    
    
    darshan_appointments_details = {}
    

    for darshan_type in darshan_types:

        darshan_appointments_details[darshan_type] = {}
        for workflow_state in darshan_appointments_states:
            
                filters = {'workflow_state': workflow_state, 'darshan_type' : darshan_type}

            
                if is_devotee:
                    filters['devoteee_profile'] = profile_id
                
                darshan_appointments_details[darshan_type][workflow_state] = frappe.db.count('Darshan Appointment', filters)


        # For multiple fields, supply fields as a list; for all fields, use '*'
        
        filters = {'darshan_type': darshan_type}
        if is_devotee:
            filters['devoteee_profile'] = profile_id
            
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