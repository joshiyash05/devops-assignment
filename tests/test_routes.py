from aceest import create_app


def make_client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})
    return app.test_client()


def test_health_check(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_swagger_docs_page(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/docs")

    assert response.status_code == 200
    assert b"SwaggerUIBundle" in response.data
    assert b"/openapi.json" in response.data


def test_openapi_spec(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/openapi.json")
    spec = response.get_json()

    assert response.status_code == 200
    assert spec["openapi"] == "3.0.3"
    assert "/clients" in spec["paths"]


def test_create_and_fetch_client(tmp_path):
    client = make_client(tmp_path)

    create_response = client.post(
        "/clients",
        json={
            "name": "Asha Kumar",
            "age": 29,
            "height_cm": 168,
            "weight_kg": 66,
            "program": "Fat Loss",
            "membership_end": "2999-12-31",
        },
    )

    assert create_response.status_code == 201
    created = create_response.get_json()["client"]
    assert created["name"] == "Asha Kumar"

    fetch_response = client.get(f"/clients/{created['id']}")

    assert fetch_response.status_code == 200
    assert fetch_response.get_json()["client"]["program"] == "Fat Loss"


def test_reject_invalid_client_payload(tmp_path):
    client = make_client(tmp_path)

    response = client.post("/clients", json={"name": "", "program": "Elite"})

    assert response.status_code == 400
    errors = response.get_json()["errors"]
    assert "name" in errors
    assert "program" in errors


def test_create_workout_and_summary(tmp_path):
    client = make_client(tmp_path)
    create_response = client.post(
        "/clients",
        json={
            "name": "Rahul Menon",
            "age": 34,
            "height_cm": 175,
            "weight_kg": 82,
            "program": "Muscle Gain",
        },
    )
    client_id = create_response.get_json()["client"]["id"]

    workout_response = client.post(
        f"/clients/{client_id}/workouts",
        json={
            "date": "2026-10-10",
            "workout_type": "Strength",
            "duration_min": 60,
            "notes": "Squat and bench session",
        },
    )

    assert workout_response.status_code == 201

    summary_response = client.get(f"/clients/{client_id}/summary")
    summary = summary_response.get_json()["summary"]

    assert summary["program"] == "Muscle Gain"
    assert summary["workouts_logged"] == 1
    assert summary["target_calories"] == 3200
