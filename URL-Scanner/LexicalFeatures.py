from imports import *

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "confirm", "account", "secure", "banking",
    "signin", "webscr", "wp-admin", "checkout", "payment", "password", "reset",
    "invoice", "support", "free", "offer", "bonus", "prize", "survey"
]
NUMERIC_FEATURE_EXPLANATIONS = {
    "url_length": "Long URLs can hide malicious parameters or mask real domains.",
    "hostname_length": "Unusually long hostnames may indicate deceptive domains.",
    "path_length": "Long paths are often used in phishing URLs to mimic real sites.",
    "dot_count": "A high number of dots might signal subdomain abuse.",
    "special_symbols": "Too many slashes may indicate redirections or obfuscation.",
    "equal_signs": "Used in query strings — often exploited in phishing links.",
    "hyphen_count": "Multiple hyphens are common in fake domains mimicking brands.",
    "underscore_count": "Rare in real domains; often used to evade detection.",
    "at_symbol_count": "'@' can be used to hide the real domain in phishing attacks.",
    "query_count": "Too many query parameters can signal suspicious behavior.",
    "colon_count": "Multiple colons may indicate port manipulation or redirection.",
    "tilde_count": "Tildes are uncommon in real URLs and may be suspicious.",
    "redirect_count": "'->' is a heuristic for redirection in URL structure.",
    "digit_count": "Malicious URLs often include many numbers to evade filters.",
    "suspicious_word_count": "Suspicious words like 'login' or 'free' suggest phishing intent."
}

BINARY_FEATURE_EXPLANATIONS = {
    "has_ip": "URLs using IP addresses are more likely to be malicious.",
    "has_port": "Explicit port numbers can indicate non-standard or shady servers.",
    "absolute_url": "Proper schemes (http/https) are normal, others might be risky.",
    "shortener": "Shortened URLs hide the real destination, often used in phishing.",
    "suspicious_tld": "TLDs like .xyz, .tk, or .top are frequently used in spam/malware.",
    "file_extension": "File types like .exe or .php can trigger downloads or exploits."
}


def count_occurrences(url, char):
    return url.count(char)

def classify_value(count, thresholds):
    if count < thresholds[0]:
        return 1
    elif thresholds[0] <= count < thresholds[1]:
        return 3
    else:
        return 5
def detect_suspicious_words(url):
    """Detects and counts suspicious words from domain/path using regex."""
    parsed = urlparse(url)
    text = (parsed.hostname or "") + (parsed.path or "")
    pattern = r'\b(' + '|'.join(SUSPICIOUS_KEYWORDS) + r')\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return len(matches), matches


def extract_feature_counts(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""

    # Suspicious word analysis (do this BEFORE building the dicts)
    susp_word_count, matched_words = detect_suspicious_words(url)

    numeric_counts = {
        'url_length': len(url),
        'hostname_length': len(hostname),
        'path_length': len(path),
        'dot_count': count_occurrences(url, '.'),
        'special_symbols': count_occurrences(url, '/'),
        'equal_signs': count_occurrences(url, '='),
        'hyphen_count': count_occurrences(url, '-'),
        'underscore_count': count_occurrences(url, '_'),
        'at_symbol_count': count_occurrences(url, '@'),
        'query_count': count_occurrences(url, '?'),
        'colon_count': count_occurrences(url, ':'),
        'tilde_count': count_occurrences(url, '~'),
        'redirect_count': count_occurrences(url, '->'),
        'digit_count': len(re.findall(r'\d', url)),
        'suspicious_word_count': susp_word_count > 0


    }

    binary_counts = {
        'has_ip': bool(re.match(r'\d+\.\d+\.\d+\.\d+', hostname)),
        'has_port': bool(re.search(r':[0-9]+', hostname)),
        'absolute_url': parsed_url.scheme in ['http', 'https'],
        'shortener': bool(re.search(r'bit\.ly|goo\.gl|tinyurl\.com', url)),
        'suspicious_tld': bool(re.search(r'\.xyz|\.tk|\.cf|\.ga|\.ml|\.top|\.info|\.biz$', hostname)),
        'file_extension': bool(re.search(r'\.exe|\.zip|\.rar|\.js|\.php$', path))
    }

    return numeric_counts, binary_counts


def classify_numeric_features(numeric_counts):
    classified_numeric = {}

    for feature, count in numeric_counts.items():
        if feature == 'url_length':
            classified_numeric[feature] = 1 if count < 51 else 3 if count < 75 else 5
        elif feature == 'hostname_length':
            classified_numeric[feature] = 1 if count < 20 else 3 if count < 31 else 5
        elif feature == 'path_length':
            classified_numeric[feature] = 1 if count < 30 else 3 if count < 51 else 5
        elif feature == 'dot_count':
            classified_numeric[feature] = 1 if count < 4 else 3 if count < 7 else 5
        elif feature == 'special_symbols':
            classified_numeric[feature] = 1 if count < 6 else 3 if count < 11 else 5
        elif feature in ['equal_signs', 'hyphen_count', 'underscore_count', 'at_symbol_count']:
            classified_numeric[feature] = 1 if count < 4 else 5
        elif feature == 'query_count':
            classified_numeric[feature] = 1 if count < 2 else 3 if count < 4 else 5
        elif feature in ['colon_count', 'tilde_count', 'redirect_count']:
            classified_numeric[feature] = 5 if count >= 2 else 1
        elif feature == 'digit_count':
            classified_numeric[feature] = 1 if count < 31 else 5
        elif feature == 'suspicious_word_count':
            classified_numeric[feature] = 1 if count == 0 else 3 if count == 1 else 5


    return classified_numeric

def classify_binary_features(binary_counts):
    classified_binary = {}

    for feature, presence in binary_counts.items():
        if feature == 'has_ip':
            classified_binary[feature] = 5 if presence else 1
        elif feature == 'has_port':
            classified_binary[feature] = 5 if presence == '80' or presence == '443' else 3 if presence else 1
        elif feature == 'absolute_url':
            classified_binary[feature] = 1 if presence else 5
        elif feature == 'shortener':
            classified_binary[feature] = 5 if presence else 1
        elif feature == 'suspicious_tld':
            classified_binary[feature] = 5 if presence else 1
        elif feature == 'file_extension':
            classified_binary[feature] = 5 if presence else 1

    return classified_binary

def classify_features(numeric_counts, binary_counts):
    classified_numeric = classify_numeric_features(numeric_counts)
    classified_binary = classify_binary_features(binary_counts)

    return {**classified_numeric, **classified_binary}


def apply_priority_coefficients(classified_features):
    coefficients = {
        '%': {5:1.2},
        'shortener': {5:1.3},
        'redirect_count': {5:1.3},
        'has_ip': {5:1.3},
        'absolute_url': {5:1.2},
        'suspicious_tld': {3: 1.2, 5: 1.3},
        'suspicious_words': {3: 1.2, 5: 1.3},
        'file_extension': {5:1.3}
    }

    adjusted_features = {}
    for feature, value in classified_features.items():
        if feature in coefficients:
            coeff = coefficients[feature]
            if isinstance(coeff, dict):  # Handles cases where coefficient varies by value
                adjusted_features[feature] = value * coeff.get(value, 1)
            else:
                adjusted_features[feature] = value * coeff
        else:
            adjusted_features[feature] = value

    return adjusted_features

def compute_lexical_feature_score(classified_features):
    total_score = sum(classified_features.values())
    avg_score = total_score / len(classified_features)
    return avg_score

def classify_features(url):
    numeric_counts, binary_counts = extract_feature_counts(url)
    classified_numeric = classify_numeric_features(numeric_counts)
    classified_binary = classify_binary_features(binary_counts)
    classified_features = {**classified_numeric, **classified_binary}

    print("\nClassified Features (Before Coefficients):", classified_features)

    adjusted_features = apply_priority_coefficients(classified_features)

    print("\nAdjusted Features (After Coefficients):", adjusted_features)
    lexical_score = compute_lexical_feature_score(adjusted_features)

    print("\nComputed Lexical Score:", lexical_score)

    return numeric_counts, binary_counts, classified_features, lexical_score

def print_feature_classification(url, output):
    numeric_counts, binary_counts, classified_features, lexical_score = classify_features(url)

    output["lexical"].append("Feature Counts and Classification:\n")

    output["lexical"].append("Numeric Features:")
    for feature, count in numeric_counts.items():
        explanation = NUMERIC_FEATURE_EXPLANATIONS.get(feature, "No explanation available.")
        risk = classified_features.get(feature, "N/A")
        output["lexical"].append(
            f"{feature}: Count = {count}, Risk Level = {risk}, Explanation = {explanation}"
        )

    output["lexical"].append("Binary Features:")
    for feature, presence in binary_counts.items():
        explanation = BINARY_FEATURE_EXPLANATIONS.get(feature, "No explanation available.")
        risk = classified_features.get(feature, "N/A")
        output["lexical"].append(
            f"{feature}: Presence = {presence}, Risk Level = {risk}, Explanation = {explanation}"
        )

    output["lexical"].append(f"\n📈 Final Lexical Feature Score: {lexical_score:.2f}")
    return lexical_score