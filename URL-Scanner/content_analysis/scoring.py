from imports import *

def apply_coefficients(features):
    """Apply priority coefficients based on high-risk indicators."""
    coefficients = {
        "Iframe": 1.2,
        "JavaScript Functions": 1.2,
        "DOM Functions": 1.05,
        "JavaScript Obfuscation": 1.1,
        "Suspicious Functions": 1.1,
        "Inline Event Handlers": 1.05,
        "Clickjacking Detection": 1.2,
        "Security Header Protection": 1.1,
        "HTTPS Usage": 1.05,
        "SSL Certificate Validity": 1.2,
        "HTML_Unavailable": 1.3,
        "High Entropy Lines": 1.1,
        "Base64 Usage": 1.1,
        "Long Base64 Strings": 1.05,
    }
    positive_indicators = ["HTTPS Usage", "SSL Certificate Validity", "Security Header Protection"]

    for feature, value in features.items():
        if isinstance(value, (int, float)):
            if value == 5 and feature in coefficients:
                features[feature] *= coefficients[feature]
            elif feature in positive_indicators:
                if value <= 1.2:
                    features[feature] *= 0.85
                elif value <= 2:
                    features[feature] *= 0.9
                # else do nothing for values 3-5
    return features

def compute_feature_score(features):
    """Compute the final feature score from nested dictionaries (html, js, headers, certificate)."""
    numeric_values = []

    for category in features.values():
        if isinstance(category, dict):
            for value in category.values():
                if isinstance(value, (int, float)):
                    numeric_values.append(value)

    if not numeric_values:
        return 0  # Avoid division by zero

    # Optional: Clip extreme values to 1-5 range
    clipped = [min(max(v, 1.0), 5.0) for v in numeric_values]
    avg_score = round(sum(clipped) / len(clipped), 2)
    return avg_score



def is_globally_reputable(features: Dict[str, float]) -> bool:
    """Infer if the URL behaves like a reputable site without hardcoding a whitelist."""
    return (
        features.get("SSL Certificate Validity", 5) <= 1.2 and
        features.get("HTTPS Usage", 5) <= 1.2 and
        features.get("Clickjacking Detection", 5) <= 2 and
        features.get("HTML Size Suspicion", 5) <= 2 and
        features.get("Base64 Usage", 5) <= 1.5 and
        features.get("High Entropy Lines", 5) <= 2 and
        features.get("Security Header Protection", 5) <= 2 and
        features.get("JavaScript Obfuscation", 5) <= 2 and
        features.get("Inline Event Handlers", 5) <= 2
    )
