"""ModuleConfig — which ERP modules are enabled for this install."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Canonical module catalogue. (key, label, category, is_core)
# Core modules cannot be disabled. nav links carry data-module="<key>".
MODULE_CATALOGUE = [
    ('dashboard', 'Dashboard', 'General', True),
    ('tools', 'Tools', 'General', False),
    ('board', 'Task Board', 'Delivery', False),
    ('projects', 'Projects', 'Delivery', False),
    ('tasks', 'Tasks', 'Delivery', False),
    ('timesheet', 'Timesheet', 'Delivery', False),
    ('tickets', 'Support Tickets', 'Delivery', False),
    ('customers', 'Customers', 'CRM & Sales', False),
    ('leads', 'Leads', 'CRM & Sales', False),
    ('opportunities', 'Opportunities', 'CRM & Sales', False),
    ('quotations', 'Quotations', 'CRM & Sales', False),
    ('sales', 'Sales Orders', 'CRM & Sales', False),
    ('enquiries', 'Enquiries', 'CRM & Sales', False),
    ('products', 'Services & Rates', 'Catalog', False),
    ('billing', 'Billing', 'Finance', False),
    ('retainers', 'Retainers', 'Finance', False),
    ('invoices', 'Invoices', 'Finance', False),
    ('expenses', 'Expenses', 'Finance', False),
    ('accounting', 'Accounting', 'Finance', False),
    ('reports', 'Reports', 'Insights', False),
    ('blog', 'Blog', 'Website', False),
    ('hr', 'Employees', 'HR', False),
    ('attendance', 'Attendance', 'HR', False),
    ('leaves', 'Leaves', 'HR', False),
    ('users', 'System Users', 'Administration', True),
    ('logs', 'System Logs', 'Administration', False),
    ('settings', 'Settings', 'Administration', True),
    ('modules', 'Modules', 'Administration', True),
]


class ModuleConfig(db.Model):
    __tablename__ = 'module_config'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60))
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    is_core = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'key': self.key,
            'label': self.label,
            'category': self.category,
            'enabled': self.enabled,
            'is_core': self.is_core,
        }

    @staticmethod
    def ensure_seeded():
        """Insert any catalogue modules missing from the table (idempotent)."""
        existing = {m.key for m in ModuleConfig.query.all()}
        created = False
        for key, label, category, is_core in MODULE_CATALOGUE:
            if key not in existing:
                db.session.add(ModuleConfig(key=key, label=label, category=category,
                                            enabled=True, is_core=is_core))
                created = True
        if created:
            db.session.commit()
