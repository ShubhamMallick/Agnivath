"""
Notification System
Sends notifications for qualified leads
"""
from datetime import datetime


class Notifier:
    """Sends notifications for qualified leads"""
    
    def __init__(self, store):
        self.store = store
    
    def send_notification(self, qualification_result: dict, lead_data: dict):
        """Send notification for a qualified lead"""
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "lead_id": qualification_result["lead_id"],
            "priority": qualification_result["priority"],
            "score": qualification_result["score"],
            "lead_name": lead_data.get("name"),
            "company": lead_data.get("company"),
            "next_action": qualification_result["next_action"],
            "message": f"New {qualification_result['priority']} priority lead: {lead_data.get('name')} from {lead_data.get('company')}"
        }
        
        # In production, this would send:
        # - Email to sales team
        # - Slack/webhook notification
        # - SMS for high priority leads
        # - Dashboard alert

        self.store.save_notification(notification)
        
        print(f"🔔 Notification sent: {notification['message']}")
        
        return notification
    
    def get_notifications(self, min_priority: str = "MEDIUM") -> list[dict]:
        """Get notifications filtered by priority"""
        return self.store.list_notifications(min_priority)
    
    def clear_notifications(self):
        """Clear all notifications"""
        return self.store.clear_notifications()
