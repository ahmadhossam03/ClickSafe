from imports import *

# Coefficient levels from Table 7
COEFFICIENTS = {
    "blacklist": 0.5,
    "lexical": 0.3,
    "host_based": 0.2,
    "content_based": 0.2
}

# Threshold for classification
THRESHOLD = 100

def calculate_feature_value(class_values: Dict[str, float]) -> float:
    """
    Compute the feature value Fi using Equation 2.
    Fi = sum(Ci * cLi) for each feature.
    """
    feature_value = sum(class_values[feature] * COEFFICIENTS[feature] for feature in class_values)
    return feature_value

def compute_detection_score(features: Dict[str, float]) -> float:
    """
    Compute the Detection Framework (DF) score using Equation 1.
    DF = sum(Fi * CLi * 20) for each feature.
    """
    df_score = 0
    for feature, value in features.items():
        if value == -1:
            alternative_value = assign_alternative_value(features)
            df_score += alternative_value * COEFFICIENTS[feature] * 20
        else:
            df_score += value * COEFFICIENTS[feature] * 20
    return df_score

def assign_alternative_value(features: Dict[str, float]) -> float:
    """
    Assign an alternative value when a feature returns -1.
    Fallback is based on other features' scores.
    """
    if features.get("blacklist", 0) >= 3:
        return 3.5  # fallback value representing "medium-high" risk
    if features.get("host_based", 0) >= 3.5:
        return 3.0
    if features.get("lexical", 0) >= 3.5:
        return 3.0
    return 2.0  # default low-medium risk fallback

def categorize_risk(df_score: float) -> str:
    if df_score < 50:
        return "Safe"
    elif df_score < 75:
        return "Suspicious"
    else:
        return "Malicious"

def detect_malicious_url(features: Dict[str, float]) -> str:
    """
    Evaluate whether a URL is malicious based on DF score.
    """
    df_score = compute_detection_score(features)
    print(f"[DEBUG] Final DF Score: {df_score}")
    return categorize_risk(df_score)

def evaluate_metrics(tp: int, tn: int, fp: int, fn: int) -> Dict[str, float]:
    """
    Compute accuracy, precision, recall, F1-score, and false positive rate.
    """
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) != 0 else 0
    precision = tp / (tp + fp) if (tp + fp) != 0 else 0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) != 0 else 0

    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1_score,
        "False Positive Rate": fpr
    }







