import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ModelMetadata:
    model_name: str
    version: str
    algorithm: str
    feature_names: List[str]
    target_name: str
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    description: str = ""
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelMetadata':
        return cls(
            model_name=data.get('model_name', ''),
            version=data.get('version', ''),
            algorithm=data.get('algorithm', ''),
            feature_names=data.get('feature_names', []),
            target_name=data.get('target_name', ''),
            metrics=data.get('metrics', {}),
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
        )

    def save_json(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, filepath: str) -> 'ModelMetadata':
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
