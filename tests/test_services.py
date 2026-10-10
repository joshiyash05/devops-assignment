import pytest

from aceest.services import (
    calculate_bmi,
    list_programs,
    membership_state,
    validate_workout_payload,
)


def test_calculate_bmi_rounds_to_two_decimals():
    assert calculate_bmi(82, 175) == 26.78


def test_calculate_bmi_rejects_invalid_height():
    with pytest.raises(ValueError):
        calculate_bmi(82, 0)


def test_list_programs_exposes_expected_programs():
    program_names = {program["name"] for program in list_programs()}

    assert {"Fat Loss", "Muscle Gain", "Beginner"} == program_names


def test_membership_state_labels_expired_and_active_dates():
    assert membership_state("2000-01-01") == "expired"
    assert membership_state("2999-12-31") == "active"


def test_validate_workout_payload_requires_positive_duration():
    errors = validate_workout_payload({"workout_type": "Cardio", "duration_min": 0})

    assert errors["duration_min"] == "Duration must be greater than zero."
