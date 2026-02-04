"""Application Constants"""

# User Roles
ROLES = {
    'ADMIN': 'admin',
    'MANAGER': 'manager',
    'EMPLOYEE': 'employee',
    'CLIENT': 'client'
}

# Task Status
TASK_STATUS = {
    'TODO': 'todo',
    'IN_PROGRESS': 'in-progress',
    'REVIEW': 'review',
    'BLOCKED': 'blocked',
    'COMPLETED': 'completed'
}

# Project Status
PROJECT_STATUS = {
    'PLANNING': 'planning',
    'ACTIVE': 'active',
    'ON_HOLD': 'on-hold',
    'COMPLETED': 'completed',
    'CANCELLED': 'cancelled'
}

# Priority Levels
PRIORITY = {
    'LOW': 'low',
    'MEDIUM': 'medium',
    'HIGH': 'high',
    'CRITICAL': 'critical'
}

# Invoice Status
INVOICE_STATUS = {
    'DRAFT': 'draft',
    'SENT': 'sent',
    'PAID': 'paid',
    'OVERDUE': 'overdue',
    'CANCELLED': 'cancelled'
}

# Payment Methods
PAYMENT_METHODS = ['cash', 'check', 'bank-transfer', 'card', 'paypal']

# File Upload Settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
