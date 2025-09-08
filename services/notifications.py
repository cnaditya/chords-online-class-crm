import requests
import logging
from datetime import datetime
from typing import Dict, Optional
from config import Config
from models.notification_log import NotificationLog
from models.base import SessionLocal

logger = logging.getLogger(__name__)

class Fast2SMSService:
    def __init__(self):
        self.api_key = Config.FAST2SMS_API_KEY
        self.base_url = Config.FAST2SMS_BASE_URL
        
    def _send_template_message(self, phone_number: str, template_id: int, variables: Dict[str, str]) -> Dict:
        """Send WhatsApp template message via Fast2SMS API"""
        if not self.api_key:
            raise ValueError("Fast2SMS API key not configured")
            
        # Format variables for API (Var1|Var2|Var3...)
        variables_string = "|".join(variables.values())
        
        url = f"{self.base_url}?authorization={self.api_key}&message_id={template_id}&numbers={phone_number}&variables_values={variables_string}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.content else {}
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Fast2SMS API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def _log_notification(self, student_id: int, phone_number: str, template_id: int, 
                         template_name: str, variables: Dict[str, str], 
                         status: str, response_data: Dict = None, error_message: str = None):
        """Log notification attempt to database"""
        db = SessionLocal()
        try:
            log_entry = NotificationLog(
                student_id=student_id,
                template_id=template_id,
                template_name=template_name,
                phone_number=phone_number,
                variables=variables,
                status=status,
                response_data=response_data,
                error_message=error_message,
                sent_at=datetime.now() if status == "sent" else None
            )
            db.add(log_entry)
            db.commit()
            return log_entry.id
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def send_fee_reminder(self, student_name: str, student_id: int, phone_number: str, 
                         package_name: str, expiry_date: str) -> bool:
        """Send fee reminder WhatsApp message"""
        variables = {
            "Var1": student_name,
            "Var2": package_name,
            "Var3": expiry_date
        }
        
        result = self._send_template_message(
            phone_number=phone_number,
            template_id=Config.TEMPLATE_FEE_REMINDER,
            variables=variables
        )
        
        status = "sent" if result["success"] else "failed"
        self._log_notification(
            student_id=student_id,
            phone_number=phone_number,
            template_id=Config.TEMPLATE_FEE_REMINDER,
            template_name="chords_fee_reminder_upi",
            variables=variables,
            status=status,
            response_data=result.get("response"),
            error_message=result.get("error")
        )
        
        return result["success"]
    
    def send_payment_receipt(self, student_name: str, student_id: int, phone_number: str,
                           amount: str, receipt_no: str, package_name: str, 
                           payment_date: str, remarks: str = "") -> bool:
        """Send payment receipt WhatsApp message"""
        variables = {
            "Var1": student_name,
            "Var2": amount,
            "Var3": receipt_no,
            "Var4": package_name,
            "Var5": payment_date,
            "Var6": remarks
        }
        
        result = self._send_template_message(
            phone_number=phone_number,
            template_id=Config.TEMPLATE_PAYMENT_RECEIPT,
            variables=variables
        )
        
        status = "sent" if result["success"] else "failed"
        self._log_notification(
            student_id=student_id,
            phone_number=phone_number,
            template_id=Config.TEMPLATE_PAYMENT_RECEIPT,
            template_name="chords_payment_receipt",
            variables=variables,
            status=status,
            response_data=result.get("response"),
            error_message=result.get("error")
        )
        
        return result["success"]