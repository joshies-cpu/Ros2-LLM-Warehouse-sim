from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Mission:
    """
    Represents a robot mission.
    """

    mission_type: str
    parameters: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mission":
        return cls(**data)