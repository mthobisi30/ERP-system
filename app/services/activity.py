"""Activity trail helper — records SDLC events against projects/clients.

Call record(...) AFTER the main operation has committed. It commits its own row
in a try/except so an audit failure can never break the underlying action.
"""
from flask_jwt_extended import get_jwt_identity

from config.database import db
from app.models.log import ActivityLog


def record(action, entity_type=None, entity_id=None, project_id=None,
           customer_id=None, summary=None):
    try:
        try:
            uid = get_jwt_identity()
        except Exception:  # noqa: BLE001 — may be called outside a JWT context
            uid = None
        log = ActivityLog(
            user_id=uid, action=action, entity_type=entity_type,
            entity_id=entity_id if entity_id else None,
            project_id=project_id if project_id else None,
            customer_id=customer_id if customer_id else None,
            summary=summary,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:  # noqa: BLE001 — never let logging break the request
        db.session.rollback()
