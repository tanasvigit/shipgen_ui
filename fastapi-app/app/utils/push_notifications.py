"""
Push notification utilities using FCM (Firebase Cloud Messaging).
"""
import os
from typing import List, Dict, Any, Optional

try:
    from pyfcm import FCMNotification
    FCM_AVAILABLE = True
except ImportError:
    FCM_AVAILABLE = False


class PushNotificationService:
    """Push notification service using FCM."""
    
    def __init__(self):
        self.fcm_api_key = os.getenv("FCM_SERVER_KEY", "")
        self.fcm_client = None
        
        if FCM_AVAILABLE and self.fcm_api_key:
            try:
                self.fcm_client = FCMNotification(api_key=self.fcm_api_key)
            except Exception:
                self.fcm_client = None
    
    def send_to_devices(
        self,
        registration_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification to multiple devices."""
        if not self.fcm_client:
            # Stub implementation - log instead of sending
            print(f"[PUSH] Would send to {len(registration_ids)} devices: {title} - {body}")
            return {
                "success": True,
                "failure": 0,
                "canonical_ids": 0,
                "results": [{"message_id": "stub"} for _ in registration_ids]
            }
        
        try:
            result = self.fcm_client.notify_multiple_devices(
                registration_ids=registration_ids,
                message_title=title,
                message_body=body,
                data_message=data or {}
            )
            return result
        except Exception as e:
            print(f"[PUSH] Error sending notification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification to a topic."""
        if not self.fcm_client:
            print(f"[PUSH] Would send to topic {topic}: {title} - {body}")
            return {"success": True, "message_id": "stub"}
        
        try:
            result = self.fcm_client.notify_topic_subscribers(
                topic_name=topic,
                message_title=title,
                message_body=body,
                data_message=data or {}
            )
            return result
        except Exception as e:
            print(f"[PUSH] Error sending to topic: {str(e)}")
            return {"success": False, "error": str(e)}


# Global push notification service
push_service = PushNotificationService()

