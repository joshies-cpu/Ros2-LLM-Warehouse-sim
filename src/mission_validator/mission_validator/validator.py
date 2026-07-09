import json


# pyrefly: ignore [missing-import]
from mission_planner.config import (
    SUPPORTED_MISSION_TYPES,
    AVAILABLE_ROUTES,
    MAX_SPEED,
)


class MissionValidator:
    """Validates mission JSON produced by the LLM."""

    def validate(self, mission_json: str) -> dict:
        # Parse JSON
        try:
            mission = json.loads(mission_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        if not isinstance(mission, dict):
            raise ValueError("Parsed JSON must be an object")

        # Check for LLM error responses
        if "error" in mission:
            raise ValueError(f"LLM returned error: {mission['error']}")

        # mission_type
        mission_type = mission.get("mission_type")

        if mission_type not in SUPPORTED_MISSION_TYPES:
            raise ValueError(
                f"Unsupported mission_type: {mission_type}"
            )

        parameters = mission.get("parameters")
        if parameters is None:
            parameters = {}
        elif not isinstance(parameters, dict):
            raise ValueError("parameters must be a JSON object")

        # Patrol validation
        if mission_type == "patrol":

            route = parameters.get("route")

            if route not in AVAILABLE_ROUTES:
                raise ValueError(f"Unknown route: {route}")

            laps = parameters.get("laps", 1)

            if laps < 1:
                raise ValueError("laps must be >= 1")

            speed = parameters.get("speed", 0.3)

            if speed > MAX_SPEED:
                raise ValueError(
                    f"Speed exceeds limit ({MAX_SPEED})"
                )

        # Navigate validation
        elif mission_type == "navigate":

            destination = parameters.get("destination")

            if destination not in AVAILABLE_ROUTES:
                raise ValueError(
                    f"Unknown destination: {destination}"
                )

            speed = parameters.get("speed", 0.3)

            if speed > MAX_SPEED:
                raise ValueError(
                    f"Speed exceeds limit ({MAX_SPEED})"
                )

        # return_home / stop need no parameters

        return mission
