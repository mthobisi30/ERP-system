"""Query Filters"""
from sqlalchemy import or_

def apply_search_filter(query, model, search_term, fields):
    """Apply search filter to query"""
    if not search_term:
        return query
    
    search = f"%{search_term}%"
    filters = [getattr(model, field).ilike(search) for field in fields if hasattr(model, field)]
    return query.filter(or_(*filters))

def apply_date_filter(query, model, field, start_date, end_date):
    """Apply date range filter"""
    if start_date:
        query = query.filter(getattr(model, field) >= start_date)
    if end_date:
        query = query.filter(getattr(model, field) <= end_date)
    return query
