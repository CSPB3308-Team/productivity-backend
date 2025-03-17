from app import db, app # imports our sqlalchemy and our app instance
from datetime import datetime, timedelta, timezone

from app.models import Users, Tasks

#### Helper Functions - used to make seeding in bulk easier #####
def get_or_create_user(username, email, first_name,last_name, password):
    # Query for the User
    user = Users.query.filter_by(username=username).first()
    # If Doesn't exist,
    if not user:
        user = Users(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        # Add it
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created!")
    else:
        print(f"User '{username}' already exists.")
    return user

# Seeds generic tasks for given user, if they don't already exist
def seed_tasks(user):
    # Query to see if the tasks exists, this is a seed so all either do or don't
    tasks = Tasks.query.filter_by(user_id=user.id).first()
    if not tasks:
        now_utc = datetime.now(timezone.utc)
        # Default Seed Tasks with some variety for testing
        tasks = [
            # Upcoming Tasks (Not yet complete)
            Tasks(user_id=user.id, task_name="Buy groceries", created_date=now_utc,
                  due_date=now_utc + timedelta(days=2), task_renewed=False, task_complete=False, task_type="short-term"),

            Tasks(user_id=user.id, task_name="Workout!", created_date=now_utc,
                  due_date=now_utc + timedelta(days=1), task_renewed=True, task_complete=False, task_type="daily"),

            Tasks(user_id=user.id, task_name="Finish the project report", created_date=now_utc - timedelta(days=5),
                  due_date=now_utc + timedelta(days=7), task_renewed=False, task_complete=False, task_type="long-term"),

            # Completed Tasks
            Tasks(user_id=user.id, task_name="Call Mom", created_date=now_utc - timedelta(days=3),
                  due_date=now_utc - timedelta(days=2), task_renewed=False, task_complete=True, task_type="short-term"),

            # Overdue
            Tasks(user_id=user.id, task_name="Pay electricity bill", created_date=now_utc - timedelta(days=10),
                  due_date=now_utc - timedelta(days=3), task_renewed=False, task_complete=False, task_type="short-term"),

            # Recurring Task (Daily)**
            Tasks(user_id=user.id, task_name="Attend morning stand-up meeting", created_date=now_utc - timedelta(days=10),
                  due_date=now_utc + timedelta(days=1), task_renewed=True, task_complete=False, task_type="daily"),

            # Long-Term Goal, not complete
            Tasks(user_id=user.id, task_name="Read 10 chapters of a book", created_date=now_utc - timedelta(days=15),
                  due_date=now_utc + timedelta(days=30), task_renewed=False, task_complete=False, task_type="long-term"),
        ]
        # Add all the tasks
        db.session.add_all(tasks)
        db.session.commit()
        print(f"Seeded tasks for {user.username}.")
    else:
        print(f"Tasks for {user.username} already exist.")

# Initialize
with app.app_context():
    # Create 3 generic users
    user1 = get_or_create_user( "adam_addams123", "user1@mail.com", "Adam", "Addams","password1",)
    user2 = get_or_create_user("bilbo_baggins420","user2@mail.com",  "Bilbo", "Baggins","password2")
    user3 = get_or_create_user("bigcarlo69", "user3@mail.com", "Carlos", "Carmen","password3")
    # Seed them with the array of tasks
    seed_tasks(user1)
    seed_tasks(user2)
    seed_tasks(user3)