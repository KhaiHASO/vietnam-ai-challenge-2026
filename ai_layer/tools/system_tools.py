import random
from typing import Dict, Any
from ai_layer.tools.registry import tool_registry
from ai_layer.tools.db_mock import load_db, save_db

@tool_registry.register(name="get_service_status")
def get_service_status(service_name: str) -> str:
    """
    Check the current operational status of a business service.
    
    :param service_name: Name of the service (e.g. payment, booking, vector_search)
    :return: A status report message
    """
    db = load_db()
    service = service_name.lower().strip()
    if service in db["services"]:
        info = db["services"][service]
        return f"Service: '{service_name}' is currently {info['status'].upper()}. Logs: {info['log']}"
    return f"Service: '{service_name}' was not found. Available services: {', '.join(db['services'].keys())}."

@tool_registry.register(name="create_support_ticket")
def create_support_ticket(title: str, service: str, description: str, priority: str = "medium") -> Dict[str, Any]:
    """
    Create a customer support ticket for unresolved technical or financial issues.
    
    :param title: Short title of the issue
    :param service: Affected service name
    :param description: Detailed description of the problem
    :param priority: Priority level (low, medium, high)
    :return: Dict containing the created ticket details and status
    """
    db = load_db()
    ticket_id = f"TCK-{random.randint(1000, 9999)}A"
    
    new_ticket = {
        "ticket_id": ticket_id,
        "title": title,
        "service": service.lower(),
        "description": description,
        "priority": priority.capitalize(),
        "status": "Open"
    }
    
    db["tickets"].append(new_ticket)
    save_db(db)
    
    return {
        "success": True,
        "message": f"Successfully created ticket {ticket_id}.",
        "ticket": new_ticket
    }

@tool_registry.register(name="check_booking_details", domain="sme")
def check_booking_details(booking_id: str) -> Dict[str, Any]:
    """
    Retrieve specific details of a booking reservation.
    
    :param booking_id: The unique booking ID (e.g. BKG-88321A)
    :return: Dict with booking information or error
    """
    db = load_db()
    bid = booking_id.upper().strip()
    if "bookings" in db:
        for booking in db["bookings"]:
            if booking["booking_id"] == bid:
                return {
                    "success": True,
                    "booking": booking
                }
    return {
        "success": False,
        "message": f"Booking ID {booking_id} not found."
    }

# --- EDUCATION TOOLS ---
@tool_registry.register(name="get_student_details", domain="education")
def get_student_details(student_id: str) -> Dict[str, Any]:
    """
    Retrieve academic profile, grades, and attendance of a student.
    
    :param student_id: The unique student ID (e.g. STU-1001)
    :return: Dict with student profile information
    """
    db = load_db()
    sid = student_id.upper().strip()
    if "students" in db:
        for student in db["students"]:
            if student["student_id"] == sid:
                return {
                    "success": True,
                    "student": student
                }
    return {
        "success": False,
        "message": f"Student ID {student_id} not found."
    }

@tool_registry.register(name="create_intervention_log", domain="education")
def create_intervention_log(student_id: str, intervention_type: str, note: str) -> Dict[str, Any]:
    """
    Log an intervention support action for a student at risk.
    
    :param student_id: Affected student ID
    :param intervention_type: Type of action (e.g., email_warning, advisory_meeting, tutoring)
    :param note: Log notes and plan
    :return: Dict with success status and logged item
    """
    db = load_db()
    sid = student_id.upper().strip()
    
    if "intervention_logs" not in db:
        db["intervention_logs"] = []
        
    log_entry = {
        "log_id": f"INT-{random.randint(1000, 9999)}",
        "student_id": sid,
        "intervention_type": intervention_type,
        "note": note,
        "status": "Logged"
    }
    db["intervention_logs"].append(log_entry)
    save_db(db)
    
    return {
        "success": True,
        "message": f"Successfully logged intervention for student {sid}.",
        "log": log_entry
    }

# --- AGRICULTURE TOOLS ---
@tool_registry.register(name="get_farm_details", domain="agriculture")
def get_farm_details(farm_id: str) -> Dict[str, Any]:
    """
    Retrieve crop profile and environmental conditions of a farm plot.
    
    :param farm_id: Unique plot/farm ID (e.g. FRM-501)
    :return: Dict containing farm information
    """
    db = load_db()
    fid = farm_id.upper().strip()
    if "farms" in db:
        for farm in db["farms"]:
            if farm["farm_id"] == fid:
                return {
                    "success": True,
                    "farm": farm
                }
    return {
        "success": False,
        "message": f"Farm ID {farm_id} not found."
    }

@tool_registry.register(name="log_treatment", domain="agriculture")
def log_treatment(crop_id: str, treatment_type: str, notes: str) -> Dict[str, Any]:
    """
    Log chemical/watering/pesticide treatment applied to a crop.
    
    :param crop_id: Unique crop ID
    :param treatment_type: Type of treatment (e.g. fungicide, irrigation, fertilizer)
    :param notes: Notes on concentration or duration
    :return: Dict with logged action details
    """
    db = load_db()
    cid = crop_id.upper().strip()
    
    if "treatment_logs" not in db:
        db["treatment_logs"] = []
        
    log_entry = {
        "log_id": f"TRT-{random.randint(1000, 9999)}",
        "crop_id": cid,
        "treatment_type": treatment_type,
        "notes": notes,
        "status": "Applied"
    }
    db["treatment_logs"].append(log_entry)
    save_db(db)
    
    return {
        "success": True,
        "message": f"Successfully logged treatment for crop {cid}.",
        "log": log_entry
    }
