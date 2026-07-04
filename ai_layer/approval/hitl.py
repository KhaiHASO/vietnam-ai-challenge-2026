import uuid
from typing import Dict, Any, List
from ai_layer.tools.db_mock import load_db, save_db, update_wallet

class HITLApprovalManager:
    def __init__(self):
        pass

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        db = load_db()
        return db.get("pending_approvals", [])

    def create_pending_approval(self, action_type: str, details: Dict[str, Any]) -> str:
        """
        Creates a pending approval entry and saves to database.
        Returns the unique approval ID.
        """
        db = load_db()
        if "pending_approvals" not in db:
            db["pending_approvals"] = []
            
        approval_id = f"APP-{uuid.uuid4().hex[:6].upper()}"
        
        entry = {
            "approval_id": approval_id,
            "action_type": action_type,
            "details": details,
            "status": "Pending"
        }
        
        db["pending_approvals"].append(entry)
        save_db(db)
        return approval_id

    def approve_action(self, approval_id: str) -> Dict[str, Any]:
        """
        Approves and executes the action.
        """
        db = load_db()
        approvals = db.get("pending_approvals", [])
        
        target = None
        for app in approvals:
            if app["approval_id"] == approval_id and app["status"] == "Pending":
                target = app
                break
                
        if not target:
            return {"success": False, "message": "Approval ID not found or already processed."}
            
        # Execute actual business logic based on action_type
        action_type = target["action_type"]
        details = target["details"]
        execution_result = {}
        
        if action_type == "cancel_booking_refund":
            booking_id = details.get("booking_id")
            refund_amount = details.get("refund_amount", 0)
            
            # Update booking status to Cancelled
            booking_found = False
            for booking in db["bookings"]:
                if booking["booking_id"] == booking_id:
                    booking["status"] = "Cancelled"
                    booking_found = True
                    break
                    
            if booking_found:
                # Add refund to wallet balance
                db["wallet"]["balance"] += refund_amount
                execution_result = {
                    "booking_id": booking_id,
                    "refund_amount": refund_amount,
                    "new_balance": db["wallet"]["balance"]
                }
            else:
                return {"success": False, "message": f"Booking ID {booking_id} not found during execution."}
                
        target["status"] = "Approved"
        save_db(db)
        
        return {
            "success": True,
            "message": f"Action {approval_id} approved and executed successfully.",
            "result": execution_result
        }

    def reject_action(self, approval_id: str) -> Dict[str, Any]:
        """
        Rejects the action.
        """
        db = load_db()
        approvals = db.get("pending_approvals", [])
        
        target = None
        for app in approvals:
            if app["approval_id"] == approval_id and app["status"] == "Pending":
                target = app
                break
                
        if not target:
            return {"success": False, "message": "Approval ID not found or already processed."}
            
        target["status"] = "Rejected"
        save_db(db)
        
        return {
            "success": True,
            "message": f"Action {approval_id} was rejected by administrator."
        }

# Global HITL Manager instance
hitl_manager = HITLApprovalManager()
