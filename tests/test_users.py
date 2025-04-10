import pytest
from app import create_app, db
from app.models import Users

@pytest.fixture
def test_app():
    app = create_app()

    # Force SQLite in-memory database for testing
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use SQLite in-memory for testing
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

def test_user_password_methods(test_app):
    with test_app.app_context():
        user = Users(
            username="secureuser",
            first_name="Secure",
            last_name="User",
            email="secure@example.com"
        )
        user.set_password("supersecret")
        db.session.add(user)
        db.session.commit()

        retrieved_user = Users.query.filter_by(username="secureuser").first()
        assert retrieved_user is not None
        assert retrieved_user.password_hash != "supersecret"
        assert retrieved_user.check_password("supersecret") is True
        assert retrieved_user.check_password("wrongpass") is False

def test_user_repr(test_app):
    with test_app.app_context():
        user = Users(
            username="repruser",
            first_name="Repr",
            last_name="User",
            email="repr@example.com"
        )
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        user_repr = repr(user)
        assert "repruser" in user_repr
        assert "repr@example.com" in user_repr
