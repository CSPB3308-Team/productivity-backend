import pytest
from app import create_app, db
from app.models import Users, Tasks
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect

# Setup test app and database
@pytest.fixture
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
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

# Edge case: Missing required fields (username and email)
def test_missing_required_fields(test_app):
    with test_app.app_context():
        user = Users(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        with pytest.raises(IntegrityError):
            db.session.add(user)
            db.session.commit()

# Edge case: Invalid email format
def test_invalid_email_format(test_app):
    with test_app.app_context():
        user = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="invalid-email",
        )
        db.session.add(user)
        with pytest.raises(IntegrityError):
            db.session.commit()

# Edge case: Duplicate username and email
def test_duplicate_username_email(test_app):
    with test_app.app_context():
        user1 = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        user1.set_password("password")
        db.session.add(user1)
        db.session.commit()

        user2 = Users(
            username="testuser",  # Duplicate username
            first_name="Another",
            last_name="User",
            email="test@example.com"  # Duplicate email
        )
        user2.set_password("password")
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()

# Edge case: User with a very long username
def test_long_username(test_app):
    with test_app.app_context():
        long_username = "a" * 100  # 100 characters long
        user = Users(
            username=long_username,
            first_name="Long",
            last_name="User",
            email="longuser@example.com"
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        retrieved_user = Users.query.filter_by(username=long_username).first()
        assert retrieved_user is not None

# Edge case: Empty task name
def test_empty_task_name(test_app):
    with test_app.app_context():
        user = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        task = Tasks(
            user_id=user.id,
            task_name="",  # Empty task name
            due_date=datetime.now(timezone.utc) + timedelta(days=3),
            task_type="short-term"
        )
        db.session.add(task)
        with pytest.raises(IntegrityError):
            db.session.commit()

# Edge case: Task with due_date in the past
def test_past_due_date(test_app):
    with test_app.app_context():
        user = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        task = Tasks(
            user_id=user.id,
            task_name="Old Task",
            due_date=datetime.now(timezone.utc) - timedelta(days=1),  # Past due date
            task_type="short-term"
        )
        db.session.add(task)
        db.session.commit()

        saved_task = Tasks.query.first()
        assert saved_task.due_date < datetime.now(timezone.utc)  # Task should have a due date in the past

# Edge case: Invalid task type (rechecking task type constraints)
def test_invalid_task_type(test_app):
    if isinstance(db.engine.dialect, sqlite_dialect):
        pytest.skip("SQLite does not enforce ENUM constraints")

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
            task_type="not-a-real-type"
        )

        db.session.add(invalid_task)
        with pytest.raises(Exception):
            db.session.commit()



