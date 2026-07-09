import os
import json
from typing import Dict, Any, List


class RouteLoader:
    """Loads and manages robot routes/destinations from a JSON configuration file."""

    def __init__(self, filepath: str = None):
        if filepath is None:
            # Default path on the system
            default_path = "/home/joshin/robo_ws/missions/routes.json"
            if os.path.exists(default_path):
                self.filepath = default_path
            else:
                # Fallback to resolving relative to the workspace directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                workspace_dir = os.path.abspath(
                    os.path.join(current_dir, "../../../")
                )
                self.filepath = os.path.join(
                    workspace_dir, "missions", "routes.json"
                )
        else:
            self.filepath = filepath

        self.routes = {}
        self.load_routes()

    def load_routes(self) -> None:
        """Load routes from the specified JSON file."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"Routes file not found at: {self.filepath}"
            )

        try:
            with open(self.filepath, "r") as f:
                self.routes = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in routes file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read routes file: {e}")

    def get_route(self, route_name: str) -> Dict[str, Any]:
        """Return the dictionary containing details of a specific route."""
        if route_name not in self.routes:
            raise KeyError(f"Route '{route_name}' not found.")
        return self.routes[route_name]

    def get_waypoints(self, route_name: str) -> List[Dict[str, Any]]:
        """Return the list of waypoints for a specific route."""
        route = self.get_route(route_name)
        return route.get("waypoints", [])
