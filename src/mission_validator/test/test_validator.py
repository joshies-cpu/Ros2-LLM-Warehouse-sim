import json
import sys
from pathlib import Path
import pytest

# Add local packages to path to resolve them
src_dir = Path(__file__).resolve().parents[2]
if src_dir.exists():
    for pkg in src_dir.iterdir():
        if pkg.is_dir() and str(pkg) not in sys.path:
            sys.path.insert(0, str(pkg))


from mission_validator.validator import MissionValidator  # noqa: E402
# pyrefly: ignore [missing-import]
from mission_planner.config import MAX_SPEED  # noqa: E402


def test_validate_valid_patrol():
    """Test validating a valid patrol mission."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "patrol",
        "parameters": {
            "route": "inspection_loop",
            "laps": 2,
            "speed": 0.4
        }
    }
    result = validator.validate(json.dumps(mission_data))
    assert result == mission_data


def test_validate_valid_navigate():
    """Test validating a valid navigate mission."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "navigate",
        "parameters": {
            "destination": "charging_station",
            "speed": 0.3
        }
    }
    result = validator.validate(json.dumps(mission_data))
    assert result == mission_data


def test_validate_valid_return_home():
    """Test validating a valid return_home mission."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "return_home"
    }
    result = validator.validate(json.dumps(mission_data))
    assert result == mission_data


def test_validate_invalid_json():
    """Test that invalid JSON syntax raises a ValueError."""
    validator = MissionValidator()
    with pytest.raises(ValueError, match="Invalid JSON"):
        validator.validate("{invalid json")


def test_validate_invalid_root_type():
    """Test that JSON with invalid root type (not an object) raises ValueError."""
    validator = MissionValidator()
    with pytest.raises(ValueError, match="Parsed JSON must be an object"):
        validator.validate(json.dumps([1, 2, 3]))


def test_validate_llm_error_response():
    """Test that LLM error responses raise a ValueError."""
    validator = MissionValidator()
    error_data = {
        "error": "Unsupported command"
    }
    with pytest.raises(ValueError, match="LLM returned error"):
        validator.validate(json.dumps(error_data))


def test_validate_unsupported_mission_type():
    """Test that unsupported mission types raise a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "fly_to_moon"
    }
    with pytest.raises(ValueError, match="Unsupported mission_type"):
        validator.validate(json.dumps(mission_data))


def test_validate_null_parameters():
    """Test that null parameters are handled and raise validation errors if needed."""
    validator = MissionValidator()
    # Patrol requires a route, so null parameters should fail because route is missing/None
    mission_data = {
        "mission_type": "patrol",
        "parameters": None
    }
    with pytest.raises(ValueError, match="Unknown route"):
        validator.validate(json.dumps(mission_data))


def test_validate_non_dict_parameters():
    """Test that non-dictionary parameters raise a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "patrol",
        "parameters": "not_a_dict"
    }
    with pytest.raises(ValueError, match="parameters must be a JSON object"):
        validator.validate(json.dumps(mission_data))


def test_validate_patrol_unknown_route():
    """Test that unknown route in patrol raises a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "patrol",
        "parameters": {
            "route": "unknown_route_name",
            "laps": 1,
            "speed": 0.3
        }
    }
    with pytest.raises(ValueError, match="Unknown route"):
        validator.validate(json.dumps(mission_data))


def test_validate_patrol_invalid_laps():
    """Test that laps less than 1 in patrol raises a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "patrol",
        "parameters": {
            "route": "inspection_loop",
            "laps": 0,
            "speed": 0.3
        }
    }
    with pytest.raises(ValueError, match="laps must be >= 1"):
        validator.validate(json.dumps(mission_data))


def test_validate_patrol_speed_limit():
    """Test that speed exceeding MAX_SPEED in patrol raises a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "patrol",
        "parameters": {
            "route": "inspection_loop",
            "laps": 1,
            "speed": MAX_SPEED + 0.1
        }
    }
    with pytest.raises(ValueError, match="Speed exceeds limit"):
        validator.validate(json.dumps(mission_data))


def test_validate_navigate_unknown_destination():
    """Test that unknown destination in navigate raises a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "navigate",
        "parameters": {
            "destination": "unknown_destination_name",
            "speed": 0.3
        }
    }
    with pytest.raises(ValueError, match="Unknown destination"):
        validator.validate(json.dumps(mission_data))


def test_validate_navigate_speed_limit():
    """Test that speed exceeding MAX_SPEED in navigate raises a ValueError."""
    validator = MissionValidator()
    mission_data = {
        "mission_type": "navigate",
        "parameters": {
            "destination": "charging_station",
            "speed": MAX_SPEED + 0.1
        }
    }
    with pytest.raises(ValueError, match="Speed exceeds limit"):
        validator.validate(json.dumps(mission_data))


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
