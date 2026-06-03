"""Project Management Routes"""
from datetime import date

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.project import Project, Sprint, Milestone, ProjectPhase, PhaseDeliverable
from app.models.projectdoc import ProjectDocument, DOC_TYPES
from app.models.schedule import TimeEntry
from app.models.settings import CompanySettings
from app.models.customer import Customer
from app.models.log import ActivityLog
from app.utils.codes import next_project_code
from app.services import pdf_service
from app.services.activity import record

projects_bp = Blueprint('projects', __name__)

_MILESTONE_FIELDS = {'sequence', 'name', 'description', 'trigger', 'amount',
                     'invoice_ref', 'payment_status', 'status'}
_PHASE_FIELDS = {'number', 'total_phases', 'title', 'phase_value', 'gate_criteria',
                 'gate_status', 'additional_scope', 'triggers_invoice_ref', 'status'}
_PROJECT_FIELDS = {'name', 'description', 'customer_id', 'opportunity_id', 'status', 'priority',
                   'project_manager_id', 'department_id', 'billing_type', 'billing_rate', 'currency',
                   'system_name', 'contract_ref', 'contract_value', 'project_type', 'scope',
                   'estimated_cost', 'estimated_hours', 'repository_url', 'live_url', 'readme',
                   'budget', 'completion_percentage', 'project_code'}
_PROJECT_DATES = {'start_date', 'end_date', 'contract_signed_date'}


def _apply_project(p, data):
    for k in _PROJECT_FIELDS:
        if k in data:
            setattr(p, k, data[k] or None if k.endswith('_id') else data[k])
    for k in _PROJECT_DATES:
        if k in data:
            setattr(p, k, _parse_date(data[k]))
    if 'tech_stack' in data:
        ts = data['tech_stack']
        p.tech_stack = ', '.join(ts) if isinstance(ts, list) else (ts or '')


def _pdf_response(pdf, ref):
    if pdf is None:
        return jsonify({'error': 'Not found'}), 404
    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename="{ref}.pdf"'})


def _parse_date(value, default=None):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Project.query
    if status:
        query = query.filter_by(status=status)
    if request.args.get('customer_id'):
        query = query.filter_by(customer_id=request.args.get('customer_id'))

    projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'projects': [p.to_dict() for p in projects.items],
        'total': projects.total
    }), 200

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    project = Project()
    _apply_project(project, data)
    if not project.project_code:
        customer = db.session.get(Customer, project.customer_id) if project.customer_id else None
        project.project_code = next_project_code(customer)
    try:
        db.session.add(project)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create project', 'detail': str(exc)}), 400
    record('project.created', 'project', project.id, project_id=project.id,
           customer_id=project.customer_id, summary=f"Project {project.project_code or project.name} created")
    return jsonify(project.to_dict()), 201

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict()), 200

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    _apply_project(project, request.get_json() or {})
    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update project', 'detail': str(exc)}), 400
    return jsonify(project.to_dict()), 200

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200

@projects_bp.route('/<project_id>/milestones', methods=['GET'])
@jwt_required()
def get_milestones(project_id):
    milestones = Milestone.query.filter_by(project_id=project_id).all()
    return jsonify([m.to_dict() for m in milestones]), 200

@projects_bp.route('/<project_id>/milestones', methods=['POST'])
@jwt_required()
def create_milestone(project_id):
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    m = Milestone(project_id=project_id, due_date=_parse_date(data.get('due_date')))
    for k in _MILESTONE_FIELDS:
        if k in data:
            setattr(m, k, data[k])
    db.session.add(m)
    db.session.commit()
    record('milestone.added', 'milestone', m.id, project_id=project_id, summary=f"Payment line '{m.name}' added")
    return jsonify(m.to_dict()), 201

@projects_bp.route('/milestones/<milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(milestone_id):
    m = Milestone.query.get_or_404(milestone_id)
    data = request.get_json() or {}
    for k in _MILESTONE_FIELDS:
        if k in data:
            setattr(m, k, data[k])
    if 'due_date' in data:
        m.due_date = _parse_date(data['due_date'], m.due_date)
    db.session.commit()
    return jsonify(m.to_dict()), 200

@projects_bp.route('/milestones/<milestone_id>', methods=['DELETE'])
@jwt_required()
def delete_milestone(milestone_id):
    m = Milestone.query.get_or_404(milestone_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Milestone deleted'}), 200

# ---- Phases & deliverables ----

@projects_bp.route('/<project_id>/phases', methods=['GET'])
@jwt_required()
def get_phases(project_id):
    phases = ProjectPhase.query.filter_by(project_id=project_id).order_by(ProjectPhase.number).all()
    return jsonify({'phases': [p.to_dict(with_deliverables=True) for p in phases]}), 200

@projects_bp.route('/<project_id>/phases', methods=['POST'])
@jwt_required()
def create_phase(project_id):
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    ph = ProjectPhase(project_id=project_id,
                      period_start=_parse_date(data.get('period_start')),
                      period_end=_parse_date(data.get('period_end')))
    for k in _PHASE_FIELDS:
        if k in data:
            setattr(ph, k, data[k])
    db.session.add(ph)
    db.session.commit()
    record('phase.added', 'phase', ph.id, project_id=project_id, summary=f"Phase added: {ph.title}")
    return jsonify(ph.to_dict(with_deliverables=True)), 201

@projects_bp.route('/phases/<phase_id>', methods=['PUT'])
@jwt_required()
def update_phase(phase_id):
    ph = ProjectPhase.query.get_or_404(phase_id)
    data = request.get_json() or {}
    for k in _PHASE_FIELDS:
        if k in data:
            setattr(ph, k, data[k])
    if 'period_start' in data:
        ph.period_start = _parse_date(data['period_start'], ph.period_start)
    if 'period_end' in data:
        ph.period_end = _parse_date(data['period_end'], ph.period_end)
    db.session.commit()
    return jsonify(ph.to_dict(with_deliverables=True)), 200

@projects_bp.route('/phases/<phase_id>', methods=['DELETE'])
@jwt_required()
def delete_phase(phase_id):
    ph = ProjectPhase.query.get_or_404(phase_id)
    PhaseDeliverable.query.filter_by(phase_id=ph.id).delete()
    db.session.delete(ph)
    db.session.commit()
    return jsonify({'message': 'Phase deleted'}), 200

@projects_bp.route('/phases/<phase_id>/deliverables', methods=['POST'])
@jwt_required()
def add_deliverable(phase_id):
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    d = PhaseDeliverable(phase_id=phase_id, name=data['name'],
                         implementation=data.get('implementation'), evidence=data.get('evidence'),
                         status=data.get('status', 'Complete'), sequence=data.get('sequence', 0))
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201

@projects_bp.route('/deliverables/<deliverable_id>', methods=['DELETE'])
@jwt_required()
def delete_deliverable(deliverable_id):
    d = PhaseDeliverable.query.get_or_404(deliverable_id)
    db.session.delete(d)
    db.session.commit()
    return jsonify({'message': 'Deliverable deleted'}), 200

# ---- Generated documents (registry + PDF) ----

@projects_bp.route('/<project_id>/documents', methods=['GET'])
@jwt_required()
def list_documents(project_id):
    docs = (ProjectDocument.query.filter_by(project_id=project_id)
            .order_by(ProjectDocument.created_at.desc()).all())
    return jsonify({'documents': [d.to_dict() for d in docs]}), 200

@projects_bp.route('/<project_id>/documents', methods=['POST'])
@jwt_required()
def create_document(project_id):
    """Create an Endorsement (END) or Project Migration Notice (PMN) record.

    Body: {doc_type: 'END'|'PMN', title, data: {...}}  -> auto-numbered ref.
    """
    data = request.get_json() or {}
    doc_type = (data.get('doc_type') or '').upper()
    if doc_type not in ('END', 'PMN'):
        return jsonify({'error': 'doc_type must be END or PMN'}), 400
    prefix = (CompanySettings.query.first().doc_ref_prefix
              if CompanySettings.query.first() else 'RSS') or 'RSS'
    ref, seq = ProjectDocument.next_ref(doc_type, prefix)
    doc = ProjectDocument(project_id=project_id, doc_type=doc_type, doc_ref=ref,
                          year=int(ref.split('-')[2]), sequence=seq,
                          title=data.get('title') or DOC_TYPES.get(doc_type),
                          data=data.get('data') or {}, created_by=get_jwt_identity())
    try:
        db.session.add(doc)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create document', 'detail': str(exc)}), 400
    record(f'document.{doc_type.lower()}', 'document', doc.id, project_id=project_id,
           summary=f"{doc.doc_ref} ({DOC_TYPES.get(doc_type, doc_type)}) generated")
    return jsonify(doc.to_dict()), 201

@projects_bp.route('/documents/<doc_id>/pdf', methods=['GET'])
@jwt_required()
def document_pdf(doc_id):
    doc = ProjectDocument.query.get_or_404(doc_id)
    if doc.doc_type == 'END':
        return _pdf_response(*pdf_service.endorsement_pdf(doc.id))
    if doc.doc_type == 'PMN':
        return _pdf_response(*pdf_service.pmn_pdf(doc.id))
    return jsonify({'error': 'No generator for this document type'}), 400

@projects_bp.route('/phases/<phase_id>/report.pdf', methods=['GET'])
@jwt_required()
def phase_report_pdf(phase_id):
    return _pdf_response(*pdf_service.milestone_report_pdf(phase_id))

@projects_bp.route('/<project_id>/brd.pdf', methods=['GET'])
@jwt_required()
def project_brd_pdf(project_id):
    return _pdf_response(*pdf_service.brd_pdf(project_id))

@projects_bp.route('/<project_id>/activity', methods=['GET'])
@jwt_required()
def project_activity(project_id):
    logs = (ActivityLog.query.filter_by(project_id=project_id)
            .order_by(ActivityLog.created_at.desc()).limit(100).all())
    return jsonify({'activity': [l.to_dict() for l in logs]}), 200

# ---- Sprints ----

@projects_bp.route('/<project_id>/sprints', methods=['GET'])
@jwt_required()
def get_sprints(project_id):
    sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.start_date.asc()).all()
    return jsonify({'sprints': [s.to_dict() for s in sprints]}), 200

@projects_bp.route('/<project_id>/sprints', methods=['POST'])
@jwt_required()
def create_sprint(project_id):
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    sprint = Sprint(
        project_id=project_id,
        name=data['name'],
        goal=data.get('goal'),
        status=data.get('status', 'planned'),
        start_date=_parse_date(data.get('start_date')),
        end_date=_parse_date(data.get('end_date')),
    )
    db.session.add(sprint)
    db.session.commit()
    return jsonify(sprint.to_dict()), 201

@projects_bp.route('/sprints/<sprint_id>', methods=['PUT'])
@jwt_required()
def update_sprint(sprint_id):
    sprint = Sprint.query.get_or_404(sprint_id)
    data = request.get_json() or {}
    for key in ('name', 'goal', 'status'):
        if key in data:
            setattr(sprint, key, data[key])
    if 'start_date' in data:
        sprint.start_date = _parse_date(data['start_date'], sprint.start_date)
    if 'end_date' in data:
        sprint.end_date = _parse_date(data['end_date'], sprint.end_date)
    db.session.commit()
    return jsonify(sprint.to_dict()), 200

# ---- Billing summary ----

@projects_bp.route('/<project_id>/unbilled-time', methods=['GET'])
@jwt_required()
def unbilled_time(project_id):
    """Summary of unbilled billable time for the project (drives invoicing)."""
    entries = (TimeEntry.query
               .filter(TimeEntry.project_id == project_id,
                       TimeEntry.billable.is_(True),
                       TimeEntry.invoiced.is_(False),
                       TimeEntry.hours > 0)
               .order_by(TimeEntry.entry_date.asc())
               .all())
    return jsonify({
        'project_id': project_id,
        'entry_count': len(entries),
        'total_hours': sum(float(e.hours or 0) for e in entries),
        'total_amount': sum(e.amount for e in entries),
        'entries': [e.to_dict() for e in entries],
    }), 200
