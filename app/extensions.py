"""Shared Flask extension instances (import these anywhere without circular imports)."""
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Storage defaults to in-memory (fine for a single process / local dev).
# In production / serverless set RATELIMIT_STORAGE_URI to a shared backend,
# e.g. redis://default:password@host:6379  — so limits hold across instances.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)
