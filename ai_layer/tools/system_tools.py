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

@tool_registry.register(name="check_booking_details")
def check_booking_details(booking_id: str) -> Dict[str, Any]:
    """
    Retrieve specific details of a booking reservation.
    
    :param booking_id: The unique booking ID (e.g. BKG-88321A)
    :return: Dict with booking information or error
    """
    db = load_db()
    bid = booking_id.upper().strip()
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
