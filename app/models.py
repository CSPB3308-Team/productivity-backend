from app import db # db = SQLAlchemy instance from init app
from datetime import datetime, timezone # used for dates
from sqlalchemy.orm import relationship # needed for associations
import bcrypt # encrypts strings, like password


# Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # we store password in a hash, see methods below

    # Hash the given password and stores in db
    def set_password(self,password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Check the given password with stored, returns true or false
    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def __repr__(self):
        return f"<User email: {self.email} - Username: {self.username}>"
    
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
