from app import db # db = SQLAlchemy instance from init app
from datetime import datetime, timezone # used for dates
from sqlalchemy.orm import relationship # needed for associations

# Simple test model
# TO DO: Modify users schema to match draft, but keep relation to `user.id` in task model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Tasks Model
class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    task_renewed = db.Column(db.Boolean, default=False)
    task_complete = db.Column(db.Boolean, default=False)

    # Task Type Enum (it needs to be one of 3 types)
    task_type = db.Column(db.Enum('short-term', 'long-term', 'daily', name='task_type_enum'), nullable=False)

    # Relationship to Users model
    user = relationship('Users', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f"<Task {self.task_name} - Due: {self.due_date} - Complete: {self.task_complete}>"
