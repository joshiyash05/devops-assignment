from datetime import date, datetime


PROGRAMS = {
    "Fat Loss": {
        "focus": "High adherence training with conditioning and calorie control.",
        "weekly_plan": [
            "Full body strength",
            "HIIT conditioning",
            "Zone 2 cardio",
            "Mobility and recovery",
        ],
        "target_calories": 2000,
    },
    "Muscle Gain": {
        "focus": "Progressive overload with higher protein and calorie surplus.",
        "weekly_plan": [
            "Push strength",
            "Pull strength",
            "Leg hypertrophy",
            "Accessory volume",
        ],
        "target_calories": 3200,
    },
    "Beginner": {
        "focus": "Technique, consistency, and basic movement confidence.",
        "weekly_plan": [
            "Foundational strength",
            "Light conditioning",
            "Core stability",
            "Mobility practice",
        ],
        "target_calories": 2400,
    },
}


def list_programs():
    return [{"name": name, **details} for name, details in PROGRAMS.items()]


def calculate_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        raise ValueError("height_cm must be greater than zero")
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 2)


def membership_state(membership_end):
    if not membership_end:
        return "unknown"

    end_date = datetime.strptime(membership_end, "%Y-%m-%d").date()
    if end_date < date.today():
        return "expired"
    return "active"


def validate_client_payload(payload):
    errors = {}

    if not str(payload.get("name", "")).strip():
        errors["name"] = "Name is required."

    program = payload.get("program", "Beginner")
    if program not in PROGRAMS:
        errors["program"] = f"Program must be one of: {', '.join(PROGRAMS)}."

    for field in ("age", "height_cm", "weight_kg"):
        value = payload.get(field)
        if value is None:
            errors[field] = "This field is required."
            continue
        try:
            if float(value) <= 0:
                errors[field] = "Value must be greater than zero."
        except (TypeError, ValueError):
            errors[field] = "Value must be numeric."

    membership_end = payload.get("membership_end")
    if membership_end:
        try:
            datetime.strptime(membership_end, "%Y-%m-%d")
        except ValueError:
            errors["membership_end"] = "Date must use YYYY-MM-DD format."

    return errors


def validate_workout_payload(payload):
    errors = {}

    if not str(payload.get("workout_type", "")).strip():
        errors["workout_type"] = "Workout type is required."

    duration = payload.get("duration_min")
    try:
        if int(duration) <= 0:
            errors["duration_min"] = "Duration must be greater than zero."
    except (TypeError, ValueError):
        errors["duration_min"] = "Duration must be a positive integer."

    workout_date = payload.get("date")
    if workout_date:
        try:
            datetime.strptime(workout_date, "%Y-%m-%d")
        except ValueError:
            errors["date"] = "Date must use YYYY-MM-DD format."

    return errors


def build_client_summary(client, workouts):
    bmi = calculate_bmi(client["weight_kg"], client["height_cm"])
    program = PROGRAMS[client["program"]]
    return {
        "client_id": client["id"],
        "name": client["name"],
        "program": client["program"],
        "bmi": bmi,
        "membership": membership_state(client.get("membership_end")),
        "target_calories": program["target_calories"],
        "workouts_logged": len(workouts),
    }
