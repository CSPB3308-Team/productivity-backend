import pytest
from app import create_app, db
from app.models import Users, Tasks
from datetime import datetime, timedelta, timezone
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect

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

def test_create_task(test_app):
    with test_app.app_context():
        user = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        user.set_password("securepass")
        db.session.add(user)
        db.session.commit()

        task = Tasks(
            user_id=user.id,
            task_name="Build backend",
            due_date=datetime.now(timezone.utc) + timedelta(days=3),
            task_type="short-term"
        )
        db.session.add(task)
        db.session.commit()

        saved_task = Tasks.query.first()
        assert saved_task is not None
        assert saved_task.task_name == "Build backend"
        assert saved_task.task_complete is False
        assert saved_task.task_renewed is False
        assert saved_task.user.username == "testuser"

def test_invalid_task_type(test_app):
    if isinstance(db.engine.dialect, sqlite_dialect):
        pytest.skip("SQLite does not enforce ENUM constraints")  # Skip if using SQLite since it doesn't enforce enum constraints

    with test_app.app_context():
        user = Users(
            username="invalidtaskuser",
            first_name="Invalid",
            last_name="Task",
            email="invalid@example.com"
        )
        user.set_password("123")
        db.session.add(user)
        db.session.commit()

        invalid_task = Tasks(
            user_id=user.id,
            task_name="Should Fail",
            task_type="not-a-real-type"  # Invalid task type
        )

        db.session.add(invalid_task)
        with pytest.raises(Exception):
            db.session.commit()

def test_task_repr(test_app):
    with test_app.app_context():
        user = Users(
            username="repro",
            first_name="Repro",
            last_name="User",
            email="repro@example.com"
        )
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()

        task = Tasks(
            user_id=user.id,
            task_name="Read logs",
            task_type="daily"
        )
        db.session.add(task)
        db.session.commit()

        assert "Read logs" in repr(task)
        assert "Complete" in repr(task)


