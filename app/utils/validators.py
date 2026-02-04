"""Data Validators"""
import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    try:
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def validate_phone(phone):
    pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$'
    return bool(re.match(pattern, phone))

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain a number"
    return True, "Valid password"
