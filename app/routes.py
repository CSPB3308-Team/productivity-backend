from flask import Blueprint, jsonify, request
from app import db
from app.models import Tasks, Users
from app.util import sign_token  # custom util import for auth

main = Blueprint("main", __name__)
# Test route, should just see the message and get a log
@main.route("/")
def home():
    print("Hello!")
    return jsonify({"message": "Flask API is running!"})

#### TASKS ROUTES #####
@main.route("/tasks", methods=["GET"])
# GET tasks
def get_tasks():
    """Returns tasks"""
    # Query Params - we can customize requests, add additional args here.
    user_id = request.args.get("user_id", type=int)
    task_complete = request.args.get("task_complete", type=bool)
    task_type = request.args.get("task_type", type=str)

    # We can specify what we want like so:
    """
      - `/tasks` => Returns all tasks, all users
      - `/tasks?user_id=1` => Returns tasks for user_id = 1
      - `/tasks?task_complete=true` => returns completed
      - `/tasks?task_type=short-term` => choose what type return
      - `/tasks?task_complete=true&user_id=1` => we can also add combinations
    """

    # Base query
    query = Tasks.query

    # Apply filters, if applicable. Note- if we add new args allowed we'll need to update this.
    if user_id:
        query = query.filter(Tasks.user_id == user_id)
    if task_complete is not None:
        query = query.filter(Tasks.task_complete == task_complete)
    if task_type:
        query = query.filter(Tasks.task_type == task_type)

    # Fetch results after filters
    tasks = query.all()

    # Convert result to JSON
    return jsonify([
        {
            "id": task.id,
            "user_id": task.user_id,
            "task_name": task.task_name,
            "created_date": task.created_date.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "task_renewed": task.task_renewed,
            "task_complete": task.task_complete,
            "task_type": task.task_type
        }
        for task in tasks
    ])

#  Create a new task
@main.route("/tasks", methods=["POST"])
def create_task():
    """Creates a new task"""
    data = request.json

    # Validate, needs required fields
    '''
    This is the required info, will use defaults for the others: 
    {
        "user_id": 3,
        "task_name": "Test missing info",
        "task_type": "long-term",
        "due_date": "2025-03-25"
    }
    '''
    required_fields = ["user_id", "task_name", "task_type", "due_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400 # bad request

    # Extract data
    user_id = data["user_id"]
    task_name = data["task_name"]
    task_type = data["task_type"]
    due_date = data.get("due_date")
    task_renewed = data.get("task_renewed", False)  # default = false
    task_complete = data.get("task_complete", False)  # default = False

    # Check if user exists
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404 # not found!

    # Create a task
    new_task = Tasks(
        user_id=user_id,
        task_name=task_name,
        task_type=task_type,
        due_date=due_date,
        task_renewed=task_renewed,
        task_complete=task_complete
    )

    # Add to adatabase
    db.session.add(new_task)
    db.session.commit()

    # Success message
    return jsonify({
        "message": "Task created successfully",
        "task": {
            "id": new_task.id,
            "user_id": new_task.user_id,
            "task_name": new_task.task_name,
            "created_date": new_task.created_date.isoformat(),
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
            "task_renewed": new_task.task_renewed,
            "task_complete": new_task.task_complete,
            "task_type": new_task.task_type
        }
    }), 201

# Update Task
@main.route("/tasks", methods=["PUT", "PATCH"])
def update_task():
    """Updates an existing task"""
    data = request.json

    # Make sure the id was passed
    task_id = data["id"]

    # If not, reject
    if not task_id:
        return jsonify({"error": "Missing task field: id"}), 400 # bad request
    
    # Check that its a valid id
    task = Tasks.query.get(task_id)
    # If not, reject
    if not task:
        return jsonify({"error": "Task not found"}), 404 # not found
    
    # Extract data and update fields, if provided
    if "task_name" in data:
        task.task_name = data["task_name"]
    if "task_type" in data:
        task.task_type = data["task_type"]
    if "due_date" in data:
        task.due_date = data["due_date"]
    if "task_renewed" in data:
        task.task_renewed = data["task_renewed"]
    if "task_complete" in data:
        task.task_complete = data["task_complete"]

    # Commit to database
    db.session.commit()

    # Return the updated details
    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "user_id": task.user_id,
            "task_name": task.task_name,
            "created_date": task.created_date.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "task_renewed": task.task_renewed,
            "task_complete": task.task_complete,
            "task_type": task.task_type
        }
    }), 200 # status = OK

# Delete Task
@main.route("/tasks", methods=["DELETE"])
def delete_task():
    """Updates an existing task"""
    data = request.json

    # Make sure the id was passed
    task_id = data["id"]

    # If not, reject
    if not task_id:
        return jsonify({"error": "Missing task field: id"}), 400 # Bad request
    
    # Check that its a valid id
    task = Tasks.query.get(task_id)
    # If not, reject
    if not task:
        return jsonify({"error": "Task not found"}), 404 # Not found
    
    # Delete task, if valid
    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200  # OK

#### USER ROUTES #####
# Login
@main.route("/login", methods=["POST"])
def login():
    """Authenticate user, return json web token for login/logout/auth"""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = Users.query.filter_by(email=email).first()
    # Check password, decoded via bcrypt method on user
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401  # Unauthorized

    # Generate JWT token with user info
    token = sign_token({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    })
    # Send token to frontend
    return jsonify({"token": token}), 200 # OK

# Create new user
@main.route("/signup", methods =["POST"])
def signup():
    data = request.json
    required_fields = ["username", "first_name", "last_name", "email", "password"]

    # Check to make sure everything is provided
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400 # bad request

    # Extract data
    username = data["username"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data.get("email")
    password = data.get("password")

    # See if user exists
    user = Users.query.filter_by(username=username).first()
    # Create or return conflict
    if not user:
        user = Users(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        # Add it
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created!")
    else:
        # Conflict message
        print(f"User '{username}' already exists.")
        return jsonify({
            "message": f"User '{username}' already exists.",
        }), 409
        # Success message
    return jsonify({
        "message": "User created successfully",
        "task": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password_hash": user.password_hash
        }
    }), 201

'''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


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



'''