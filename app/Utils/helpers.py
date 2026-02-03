"""Helper Functions"""
from datetime import datetime, timedelta
import uuid

def generate_code(prefix, length=8):
    """Generate unique code with prefix"""
    return f"{prefix}-{str(uuid.uuid4())[:length].upper()}"

def calculate_date_range(period):
    """Calculate date range for common periods"""
    today = datetime.now()
    if period == 'today':
        return today.replace(hour=0, minute=0), today
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == 'month':
        start = today.replace(day=1)
        return start, today
    elif period == 'year':
        start = today.replace(month=1, day=1)
        return start, today
    return None, None

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£'}
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:,.2f}"
