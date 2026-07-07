"""
Configuration settings for the Mission Planner.

This file contains all configurable parameters used throughout the
mission planning pipeline. Keeping configuration separate from the
application logic makes the system easier to maintain, extend, and test.
"""

# -----------------------
# Robot Settings
# -----------------------

DEFAULT_SPEED = 0.3      # meters/second
MAX_SPEED = 0.5

DEFAULT_LAPS = 1


# -----------------------
# Supported Mission Types
# -----------------------

SUPPORTED_MISSION_TYPES = [
    "patrol",
    "navigate",
    "return_home",
    "stop",
]


# -----------------------
# Available Routes
# -----------------------

AVAILABLE_ROUTES = {
    "inspection_loop": "Indoor inspection route around the facility.",
    "warehouse_loop": "Patrol route covering the warehouse aisles.",
    "charging_station": "Robot charging location.",
    "loading_dock": "Inspection route around the loading dock.",
}


# -----------------------
# LLM Configuration
# -----------------------

LLM_PROVIDER = "ollama"

OLLAMA_HOST = "http://localhost:11434"

OLLAMA_MODEL = "qwen2.5:7b"

OLLAMA_TEMPERATURE = 0.0

REQUEST_TIMEOUT = 30


# -----------------------
# Application Settings
# -----------------------

OUTPUT_FORMAT = "json"

LOG_LEVEL = "INFO"