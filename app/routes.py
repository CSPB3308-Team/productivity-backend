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
# TO DO: Create, Update, and delete


#### USER ROUTES #####
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
    return jsonify({"token": token}), 200 
