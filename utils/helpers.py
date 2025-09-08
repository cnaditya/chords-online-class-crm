from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import string

def generate_receipt_number() -> str:
    """Generate unique receipt number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"CMA{timestamp}{random_part}"

def format_currency(amount: float) -> str:
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def calculate_expiry_date(start_date: datetime, duration_months: int) -> datetime:
    """Calculate package expiry date"""
    return start_date + relativedelta(months=duration_months)

def get_days_until_expiry(expiry_date: datetime) -> int:
    """Get number of days until expiry"""
    return (expiry_date.date() - datetime.now().date()).days