"""Pytest fixtures.

Tests run against a real Postgres database (the models use native UUID/JSONB).
Set TEST_DATABASE_URL to a throwaway database, e.g.:

    TEST_DATABASE_URL=postgresql://erp@/erptest?host=/tmp&port=55432 pytest

If TEST_DATABASE_URL is not set, the suite is skipped.
"""
import os
import uuid

import pytest

TEST_DB = os.getenv('TEST_DATABASE_URL')


@pytest.fixture(scope='session')
def flask_app():
    if not TEST_DB:
        pytest.skip('TEST_DATABASE_URL not set')
    os.environ['DATABASE_URL'] = TEST_DB
    os.environ['FLASK_ENV'] = 'production'  # quiet SQL echo
    import index
    from app.extensions import limiter
    limiter.enabled = False  # don't rate-limit tests
    index.app.config['TESTING'] = True
    return index.app


@pytest.fixture
def app(flask_app):
    from config.database import db
    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    """Factory: create a user and return {id, email, token, password}."""
    from config.database import db
    from app.models.user import User
    from flask_bcrypt import generate_password_hash
    from flask_jwt_extended import create_access_token

    def _make(role='employee', position=None, password='Password123', email=None):
        with app.app_context():
            user = User(
                email=email or f'{uuid.uuid4().hex[:10]}@test.co.za',
                username=uuid.uuid4().hex[:10],
                password_hash=generate_password_hash(password).decode('utf-8'),
                role=role,
                position=position,
                is_active=True,
            )
            db.session.add(user)
            db.session.commit()
            return {
                'id': str(user.id),
                'email': user.email,
                'password': password,
                'token': create_access_token(identity=str(user.id)),
            }
    return _make


def auth(token):
    return {'Authorization': f'Bearer {token}'}
