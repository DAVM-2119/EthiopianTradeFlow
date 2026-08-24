from typing import Dict, Any, List

def validate_and_clean_features(raw_features: Dict[str, Any], required_features: List[str], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and cleans raw input dictionary for ML inference.
    Ensures missing values fall back safely to configured defaults.
    """
    cleaned = {}
    for feat in required_features:
        val = raw_features.get(feat)
        if val is None or val == '':
            cleaned[feat] = defaults.get(feat, 0.0)
        else:
            try:
                cleaned[feat] = float(val)
            except (ValueError, TypeError):
                cleaned[feat] = defaults.get(feat, 0.0)
    return cleaned
