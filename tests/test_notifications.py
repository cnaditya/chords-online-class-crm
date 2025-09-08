import unittest
from unittest.mock import patch, MagicMock
from services.notifications import Fast2SMSService
from config import Config

class TestFast2SMSService(unittest.TestCase):
    
    def setUp(self):
        self.service = Fast2SMSService()
    
    @patch('services.notifications.requests.get')
    @patch('services.notifications.SessionLocal')
    def test_send_fee_reminder_success(self, mock_session, mock_requests):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        # Test fee reminder
        result = self.service.send_fee_reminder(
            student_name="John Doe",
            student_id=1,
            phone_number="9876543210",
            package_name="3 Months - 24 Classes",
            expiry_date="2024-01-15"
        )
        
        self.assertTrue(result)
        mock_requests.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('services.notifications.requests.get')
    @patch('services.notifications.SessionLocal')
    def test_send_payment_receipt_success(self, mock_session, mock_requests):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        # Test payment receipt
        result = self.service.send_payment_receipt(
            student_name="John Doe",
            student_id=1,
            phone_number="9876543210",
            amount="5000",
            receipt_no="CMA202401011234",
            package_name="3 Months - 24 Classes",
            payment_date="01-01-2024",
            remarks="Payment received"
        )
        
        self.assertTrue(result)
        mock_requests.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('services.notifications.requests.get')
    @patch('services.notifications.SessionLocal')
    def test_api_failure(self, mock_session, mock_requests):
        # Mock API failure
        mock_requests.side_effect = Exception("API Error")
        
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        # Test fee reminder with API failure
        result = self.service.send_fee_reminder(
            student_name="John Doe",
            student_id=1,
            phone_number="9876543210",
            package_name="3 Months - 24 Classes",
            expiry_date="2024-01-15"
        )
        
        self.assertFalse(result)
        mock_db.add.assert_called_once()  # Should still log the attempt
        mock_db.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()