"""Data Formatters"""
from datetime import datetime

def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime object"""
    if isinstance(dt, datetime):
        return dt.strftime(format)
    return dt

def format_phone(phone):
    """Format phone number"""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def truncate_string(text, length=50):
    """Truncate string to specified length"""
    if len(text) <= length:
        return text
    return text[:length-3] + "..."
