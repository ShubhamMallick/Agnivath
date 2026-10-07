"""
Notification System
Sends notifications for qualified leads
"""
from typing import Dict, List
import json
from datetime import datetime


class Notifier:
    """Sends notifications for qualified leads"""
    
    def __init__(self):
        self.notifications = []  # In-memory storage for demo
    
    def send_notification(self, qualification_result: Dict, lead_data: Dict):
        """Send notification for a qualified lead"""
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "lead_id": qualification_result["lead_id"],
            "priority": qualification_result["priority"],
            "score": qualification_result["score"],
            "lead_name": lead_data.get("name"),
            "company": lead_data.get("company"),
            "email": lead_data.get("email"),
            "next_action": qualification_result["next_action"],
            "message": f"New {qualification_result['priority']} priority lead: {lead_data.get('name')} from {lead_data.get('company')}"
        }
        
        self.notifications.append(notification)
        
        # In production, this would send:
        # - Email to sales team
        # - Slack/webhook notification
        # - SMS for high priority leads
        # - Dashboard alert
        
        print(f"🔔 Notification sent: {notification['message']}")
        
        return notification
    
    def get_notifications(self, min_priority: str = "MEDIUM") -> List[Dict]:
        """Get notifications filtered by priority"""
        priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        min_priority_score = priority_order.get(min_priority, 0)
        
        filtered = [
            n for n in self.notifications
            if priority_order.get(n["priority"], 0) >= min_priority_score
        ]
        
        return sorted(filtered, key=lambda x: x["timestamp"], reverse=True)
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []
