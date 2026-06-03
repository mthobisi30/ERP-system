"""Human-meaningful reference codes (so clients see MPIA-001, not a UUID)."""
import re

from app.models.customer import Customer
from app.models.project import Project


def _base_from_name(name):
    """Derive a short, readable code base from a company name.

    "MPIA Services (PTY) Ltd" -> "MPIA";  "Acme" -> "ACME";  "AB Co" -> "ABC".
    """
    words = re.findall(r'[A-Za-z0-9]+', name or '')
    if not words:
        return 'CLI'
    first = words[0].upper()
    if len(first) >= 3:
        return first[:6]
    return (''.join(w[0] for w in words[:4]).upper() or first)[:6]


def next_customer_code(company_name):
    """Unique client code derived from the name (CLIENT, CLIENT2, …)."""
    base = _base_from_name(company_name)
    code, i = base, 1
    while Customer.query.filter_by(customer_code=code).first():
        i += 1
        code = f"{base}{i}"
    return code


def next_project_code(customer):
    """Per-client sequential project code, e.g. MPIA-001, MPIA-002 (PRJ-001 if no client)."""
    prefix = (customer.customer_code if customer and customer.customer_code else 'PRJ')
    n = 1
    while True:
        code = f"{prefix}-{n:03d}"
        if not Project.query.filter_by(project_code=code).first():
            return code
        n += 1
