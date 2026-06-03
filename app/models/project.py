"""
Project Management Models
"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_code = db.Column(db.String(50), unique=True)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    opportunity_id = db.Column(UUID(as_uuid=True), db.ForeignKey('opportunities.id'))
    status = db.Column(db.String(50), default='planning')
    priority = db.Column(db.String(20), default='medium')
    project_manager_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    department_id = db.Column(UUID(as_uuid=True), db.ForeignKey('departments.id'))
    # Billing: fixed_price | time_and_materials | retainer
    billing_type = db.Column(db.String(30), default='time_and_materials')
    billing_rate = db.Column(db.Numeric(10, 2))  # fallback hourly rate for T&M
    currency = db.Column(db.String(10), default='ZAR')
    # Contract details (drive generated documents)
    system_name = db.Column(db.String(250))           # e.g. "Inspection Lifecycle Management System (ILMS)"
    contract_ref = db.Column(db.String(80))           # e.g. "MPIA-BRD-002 v2.0"
    contract_signed_date = db.Column(db.Date)
    contract_value = db.Column(db.Numeric(15, 2))
    # Configuration (what kind of project this is)
    project_type = db.Column(db.String(60))            # Custom Software | Web App | Mobile App | ...
    tech_stack = db.Column(db.Text)                    # comma-separated tags
    scope = db.Column(db.Text)                         # scope of work (markdown)
    estimated_cost = db.Column(db.Numeric(15, 2))
    estimated_hours = db.Column(db.Numeric(10, 2))
    repository_url = db.Column(db.String(300))
    live_url = db.Column(db.String(300))
    readme = db.Column(db.Text)                        # README / project notes (markdown)
    budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2), default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    completion_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'project_code': self.project_code,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'opportunity_id': str(self.opportunity_id) if self.opportunity_id else None,
            'status': self.status,
            'priority': self.priority,
            'billing_type': self.billing_type,
            'billing_rate': float(self.billing_rate) if self.billing_rate else None,
            'currency': self.currency,
            'system_name': self.system_name,
            'contract_ref': self.contract_ref,
            'contract_signed_date': self.contract_signed_date.isoformat() if self.contract_signed_date else None,
            'contract_value': float(self.contract_value) if self.contract_value else None,
            'project_type': self.project_type,
            'tech_stack': [t.strip() for t in (self.tech_stack or '').split(',') if t.strip()],
            'scope': self.scope,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost is not None else None,
            'estimated_hours': float(self.estimated_hours) if self.estimated_hours is not None else None,
            'repository_url': self.repository_url,
            'live_url': self.live_url,
            'readme': self.readme,
            'budget': float(self.budget) if self.budget else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'completion_percentage': self.completion_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Sprint(db.Model):
    __tablename__ = 'sprints'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.Text)
    status = db.Column(db.String(50), default='planned')  # planned | active | completed
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'name': self.name,
            'goal': self.goal,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

class ProjectTeam(db.Model):
    __tablename__ = 'project_team'
    
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(100))
    hourly_rate = db.Column(db.Numeric(10, 2))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

class Milestone(db.Model):
    """A line in the project payment schedule (Deposit / Milestone N / Final / Website)."""
    __tablename__ = 'milestones'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    sequence = db.Column(db.Integer, default=0)        # ordering in the schedule
    name = db.Column(db.String(200), nullable=False)   # "Deposit", "Milestone 1", "Final"
    description = db.Column(db.Text)
    trigger = db.Column(db.Text)                        # "Phase 1 gate acceptance"
    amount = db.Column(db.Numeric(15, 2))
    invoice_ref = db.Column(db.String(50))             # "RSS-INV-2026-003"
    # payment_status: paid | pending | upcoming | delivered | cancelled
    payment_status = db.Column(db.String(30), default='upcoming')
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')
    completion_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'sequence': self.sequence,
            'name': self.name,
            'description': self.description,
            'trigger': self.trigger,
            'amount': float(self.amount) if self.amount is not None else None,
            'invoice_ref': self.invoice_ref,
            'payment_status': self.payment_status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
        }


class ProjectPhase(db.Model):
    """A delivery phase — drives the Milestone/Phase Completion Report."""
    __tablename__ = 'project_phases'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    number = db.Column(db.Integer)                     # this phase number
    total_phases = db.Column(db.Integer)               # "of M"
    title = db.Column(db.String(250), nullable=False)  # "Mobile Data Capture, Offline Engine & Geospatial"
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    phase_value = db.Column(db.Numeric(15, 2))
    gate_criteria = db.Column(db.Text)
    gate_status = db.Column(db.String(120))            # "Met and exceeded"
    additional_scope = db.Column(db.Text)
    triggers_invoice_ref = db.Column(db.String(50))
    status = db.Column(db.String(30), default='in_progress')  # in_progress | complete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, with_deliverables=False):
        data = {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'number': self.number,
            'total_phases': self.total_phases,
            'title': self.title,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'phase_value': float(self.phase_value) if self.phase_value is not None else None,
            'gate_criteria': self.gate_criteria,
            'gate_status': self.gate_status,
            'additional_scope': self.additional_scope,
            'triggers_invoice_ref': self.triggers_invoice_ref,
            'status': self.status,
        }
        if with_deliverables:
            items = PhaseDeliverable.query.filter_by(phase_id=self.id).order_by(PhaseDeliverable.sequence).all()
            data['deliverables'] = [d.to_dict() for d in items]
        return data


class PhaseDeliverable(db.Model):
    __tablename__ = 'phase_deliverables'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phase_id = db.Column(UUID(as_uuid=True), db.ForeignKey('project_phases.id'), nullable=False)
    sequence = db.Column(db.Integer, default=0)
    name = db.Column(db.String(250), nullable=False)
    implementation = db.Column(db.Text)
    evidence = db.Column(db.String(250))
    status = db.Column(db.String(60), default='Complete')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'phase_id': str(self.phase_id),
            'sequence': self.sequence,
            'name': self.name,
            'implementation': self.implementation,
            'evidence': self.evidence,
            'status': self.status,
        }
