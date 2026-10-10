from flask import Blueprint, jsonify, request

from aceest import services
from aceest.storage import (
    create_client,
    create_workout,
    get_client,
    list_clients,
    list_workouts,
)


bp = Blueprint("api", __name__)


@bp.get("/")
def index():
    return jsonify(
        {
            "message": "Welcome to ACEest Fitness & Gym API",
            "endpoints": [
                "/health",
                "/programs",
                "/clients",
                "/clients/<id>",
                "/clients/<id>/summary",
                "/clients/<id>/workouts",
            ],
        }
    )


@bp.get("/health")
def health_check():
    return jsonify({"service": "ACEest Fitness API", "status": "ok"})


@bp.get("/programs")
def programs():
    return jsonify({"programs": services.list_programs()})


@bp.get("/clients")
def clients_index():
    return jsonify({"clients": list_clients()})


@bp.post("/clients")
def clients_create():
    payload = request.get_json(silent=True) or {}
    errors = services.validate_client_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    client = create_client(payload)
    return jsonify({"client": client}), 201


@bp.get("/clients/<int:client_id>")
def clients_show(client_id):
    client = get_client(client_id)
    if client is None:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"client": client})


@bp.get("/clients/<int:client_id>/summary")
def clients_summary(client_id):
    client = get_client(client_id)
    if client is None:
        return jsonify({"error": "Client not found"}), 404

    workouts = list_workouts(client_id)
    return jsonify({"summary": services.build_client_summary(client, workouts)})


@bp.get("/clients/<int:client_id>/workouts")
def workouts_index(client_id):
    if get_client(client_id) is None:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"workouts": list_workouts(client_id)})


@bp.post("/clients/<int:client_id>/workouts")
def workouts_create(client_id):
    if get_client(client_id) is None:
        return jsonify({"error": "Client not found"}), 404

    payload = request.get_json(silent=True) or {}
    errors = services.validate_workout_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    workout = create_workout(client_id, payload)
    return jsonify({"workout": workout}), 201
