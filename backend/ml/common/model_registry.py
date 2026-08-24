import os
import threading
from typing import Dict, Any, Optional
import joblib
from .model_metadata import ModelMetadata

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')

class ModelRegistry:
    """
    Thread-safe Model Registry tracking registered model files, metadata, and active versions.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelRegistry, cls).__new__(cls)
                cls._instance._registry = {}
                cls._instance._loaded_models = {}
            return cls._instance

    def register_model(self, name: str, version: str, model_obj: Any, metadata: ModelMetadata, model_path: str):
        key = f"{name}:{version}"
        self._registry[key] = {
            'name': name,
            'version': version,
            'metadata': metadata,
            'path': model_path,
        }
        self._loaded_models[key] = model_obj
        if metadata.is_active:
            self._registry[f"{name}:active"] = key

    def get_active_model(self, name: str) -> Optional[Dict[str, Any]]:
        active_key = self._registry.get(f"{name}:active")
        if not active_key:
            # Attempt to auto-discover model file from artifacts directory
            model_file = os.path.join(MODEL_DIR, f"{name}-v1.joblib")
            meta_file = os.path.join(MODEL_DIR, f"{name}-v1.json")
            if os.path.exists(model_file) and os.path.exists(meta_file):
                try:
                    model_obj = joblib.load(model_file)
                    metadata = ModelMetadata.load_json(meta_file)
                    self.register_model(name, metadata.version, model_obj, metadata, model_file)
                    active_key = f"{name}:{metadata.version}"
                except Exception as e:
                    print(f"Failed to auto-load model {name}: {e}")
                    return None
            else:
                return None

        reg_info = self._registry.get(active_key)
        if not reg_info:
            return None

        return {
            'name': reg_info['name'],
            'version': reg_info['version'],
            'model': self._loaded_models.get(active_key),
            'metadata': reg_info['metadata'],
        }

    def list_models(self) -> Dict[str, Any]:
        result = {}
        for key, info in self._registry.items():
            if not key.endswith(':active'):
                result[key] = info['metadata'].to_dict()
        return result


model_registry = ModelRegistry()
