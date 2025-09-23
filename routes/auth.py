from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("password"):
        return jsonify({"error": "Name and password required"}), 400

    user, token = AuthService.register_user(data["name"], data["password"])

    if user is None:
        return jsonify({"error": "User already exists"}), 409

    return jsonify({
        "message": "User created",
        "access_token": token,
        "user": user.to_dict()
    }), 201

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("password"):
        return jsonify({"error": "Missing name or password"}), 400

    user, token = AuthService.authenticate_user(data["name"], data["password"])

    if user and token:
        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": user.to_dict()
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401
