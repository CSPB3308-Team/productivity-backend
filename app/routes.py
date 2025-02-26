from flask import Blueprint, jsonify

main = Blueprint("main", __name__)

# Test route, should just see the message and get a log
@main.route("/")
def home():
    print("Hello!")
    return jsonify({"message": "Flask API is running!"})