import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/chords_crm.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FAST2SMS_API_KEY = os.getenv('FAST2SMS_API_KEY')
    FAST2SMS_BASE_URL = os.getenv('FAST2SMS_BASE_URL', 'https://www.fast2sms.com/dev/whatsapp')
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kolkata')
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'data/uploads')
    
    # Fast2SMS Template IDs
    TEMPLATE_FEE_REMINDER = 5170
    TEMPLATE_PAYMENT_RECEIPT = 5171
    
    # Academy Details
    ACADEMY_NAME = "Chords Music Academy"
    INSTRUCTORS = ["Aditya", "Brahmani"]
    INSTRUMENTS = ["Piano", "Keyboard", "Guitar", "Carnatic Vocal"]
    UPI_ID = "7702031818"
    SUPPORT_PHONE = "+917981585309"
    
    # Package Options
    PACKAGES = {
        "1_month_8": {"name": "1 Month - 8 Classes", "classes": 8, "duration_months": 1},
        "3_months_24": {"name": "3 Months - 24 Classes", "classes": 24, "duration_months": 3},
        "6_months_48": {"name": "6 Months - 48 Classes", "classes": 48, "duration_months": 6},
        "1_year_96": {"name": "1 Year - 96 Classes", "classes": 96, "duration_months": 12}
    }