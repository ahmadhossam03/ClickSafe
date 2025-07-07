from imports import *
from content_analysis.html_analysis import fetch_html, analyze_content, detect_iframes
from content_analysis.javascript_analysis import fetch_javascript, analyze_javascript
from content_analysis.ssl_checks import check_https_from_response, get_certificate
from content_analysis.security_headers import check_security_headers_from_response
from content_analysis.scoring import apply_coefficients, compute_feature_score, is_globally_reputable
from content_analysis.reporting import print_results, print_results_beforecoeffient, print_results_js
from typing import List, Dict, Any


MAX_JS_LENGTH = 150000  # or whatever threshold you prefer




def is_ip(url):
    """Check if the URL is an IP address and whether it's private/reserved."""
    try:
        hostname = urlparse(url).hostname
        if hostname is None:
            return False
        ip_obj = ipaddress.ip_address(hostname)
        # True if IP and is private/reserved/loopback/multicast
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast or ip_obj.is_reserved
    except ValueError:
        return False


def get_risk_label(score: float) -> str:
    """Maps numeric scores to human-readable severity labels."""
    if score <= 1:
        return "Safe"
    elif score == 3:
        return "Suspicious"
    elif score == 4:
        return "High"
    else:
        return "Malicious"

def format_features_with_counts_and_scores(features: dict, counts: dict) -> List[Dict[str, Any]]:
    feature_descriptions = {
        "Popup Windows": "Opening windows can trick users or simulate phishing.",
        "JavaScript Obfuscation": "Obfuscation often hides malicious behavior.",
        "Clickjacking Detection": "Suspicious iframe behavior detected via styling or nesting.",
        "Meta Refresh": "Meta tag detected with potential redirect.",
        "Insecure Form": "Form submitted over insecure HTTP connection.",
        "Redirect Status": "HTTP status indicates potential redirection.",
        "HTML Size Suspicion": "Page length indicates suspicious or overly small/large size.",
    }

    table = []
    for feature, score in features.items():
        label = get_risk_label(score)
        explanation = feature_descriptions.get(
            feature,
            "Low risk or safe usage." if label == "Safe"
            else "Potential risk detected." if label in {"Low", "Medium"}
            else "Suspicious or risky behavior detected."
        )

        table.append({
            "feature": feature,
            "count": counts.get(feature, 0),
            "score": score,
            "severity": label,
            "explanation": explanation
        })
    return table



def generate_explanation(feature, score):
    if score == 1:
        return "Low risk or safe usage."
    elif score == 2:
        return "Mildly suspicious activity."
    elif score == 3:
        return "Moderate suspicion."
    elif score == 4:
        return "Strong indicators of phishing."
    elif score == 5:
        return "Highly suspicious or dangerous pattern."
    else:
        return "N/A"

def content_based_classification(url, output):
    """Main function for content-based classification."""
    print(f"\nAnalyzing URL: {url}\n")

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        response = None

    html = response.text if response else None
    https_score = check_https_from_response(response)
    cert_info, cert_score = get_certificate(url)

    if is_ip(url):
        print("Detected IP-based URL. Skipping classification.")
        return -1, {}  # Skip IP-based URLs

    features = {}
    html = fetch_html(url)

    if html is None:
        print("HTML could not be fetched — assigning HTML_Unavailable risk score.")
        features["HTML_Unavailable"] = 5
        counts = {}
    else:
        features_tmp, counts = analyze_content(html, url)
        features.update(features_tmp)

    #Clickjacking check — always assigns a score
    print("Checking for Clickjacking Signs...")
    if html is not None:
        clickjacking_score, clickjacking_result, iframe_evidence = detect_iframes(html)
        verdict = "Malicious" if clickjacking_score == 5 else "Suspicious" if clickjacking_score >= 3 else "Safe"

        features["Clickjacking Detection"] = clickjacking_score
        counts["Clickjacking Detection"] = len(iframe_evidence)  #Add iframe count for report

        print(clickjacking_result)
        for iframe in iframe_evidence:
            print("Suspicious Iframe Detected:")
            print(iframe["iframe"])
            print("Flags:", ", ".join(iframe["flags"]))
            print("-" * 20)
    else:
        clickjacking_score = 5  # High suspicion if HTML can't be inspected
        clickjacking_result = "Could not inspect HTML for iframes"
        iframe_evidence = []
        verdict = "Malicious"  # Still assign verdict here
    print(clickjacking_result)
    features["Clickjacking Detection"] = clickjacking_score
    counts["Clickjacking Detection"] = len(iframe_evidence)

    print("Checking HTTPS Security...")
    features["HTTPS Usage"] = check_https_from_response(response)

    print("Retrieving SSL Certificate Details...")
    certificate_info, cert_score = get_certificate(url)
    for key, value in certificate_info.items():
        print(f"{key}: {value}")
    features["SSL Certificate Validity"] = cert_score

    # Include clickjacking score as a new feature
    features["Clickjacking Detection"] = clickjacking_score

    #  Add security header score to features
    features["HTTPS Usage"] = https_score
    print(https_score)
    features["SSL Certificate Validity"] = cert_score

    # Print results
    print_results_beforecoeffient(html, counts, features)

    # Fetch and analyze JavaScript
    js_scripts = fetch_javascript(url, html=html)
    if js_scripts:
        js_features, js_counts = analyze_javascript(js_scripts, url)
        features.update(js_features)  # Merge JS features into main feature set
        print_results_js(js_counts, js_features)

    # Apply coefficients and compute final score
    features = apply_coefficients(features)
    if is_globally_reputable(features):
        print("Reputable behavior detected — softening score impact.")
        for key in features:
            if isinstance(features[key], (int, float)) and features[key] > 1.2:
                features[key] *= 0.85  # soften penalties

    print_results(html, counts, features)
    ssl_info_formatted = [
        {
            "key": k,
            "raw": v,
            "score": cert_score,
            "explanation": "SSL certificate detail" if k != "Error" else "SSL check failed"
        } for k, v in certificate_info.items()
    ]

    # Add HTTPS Usage and Certificate Validity explicitly
    ssl_info_formatted.append({
        "key": "HTTPS Usage",
        "raw": "Enabled" if https_score <= 1.2 else "Disabled or partial",
        "score": https_score,
        "explanation": "Low risk or safe usage." if https_score <= 1 else "Potential HTTPS weakness or absence."
    })

    ssl_info_formatted.append({
        "key": "SSL Certificate Validity",
        "raw": "Valid" if cert_score <= 1.2 else "Invalid or suspicious",
        "score": cert_score,
        "explanation": "Low risk or safe usage." if cert_score <= 1 else "Potential risk with certificate."
    })


    iframe_logs = [
        {
            "feature": "Suspicious Iframe",
            "count": 1,
            "score": clickjacking_score,
            "explanation": ", ".join(snippet["flags"])[:300]
        }
        for snippet in iframe_evidence
    ]

    # First, structure logs
    logs_structured = {
        "html_analysis": [
            row for row in format_features_with_counts_and_scores(features, counts)
            if row["feature"] in {
                "Iframe", "Mailto",
                "HTML Size Suspicion", "Meta Refresh", "Insecure Form", "Redirect Status", "Suspicious Iframe"
            }
        ]+ iframe_logs,
        #"javascript_analysis": format_features_with_counts_and_scores(js_features, js_counts) if js_scripts else [],
        "javascript_analysis": format_features_with_counts_and_scores(js_features.copy(), js_counts.copy()) if js_scripts else [],
        #"security_headers": security_headers_formatted,
        "ssl_certificate": ssl_info_formatted  # Now includes HTTPS Usage and Certificate Validity
    }
    # Remove Clickjacking Detection and other ignored features from scoring but keep in features/logs
    features_for_scoring = {
        k: v for k, v in features.items()
        if k not in {
            "JavaScript Functions",
            "DOM Functions",
            "JavaScript Obfuscation",
            "DOM Functions"
        }
    }


    # Then compute score from structured logs
    return_score = compute_feature_score({
        "html": features_for_scoring,
        "js": js_features if js_scripts else {},
        #"headers": {"Security Header Protection": header_score},
        "certificate": {"SSL Certificate Validity": cert_score}
    })

    if output is not None:
        output["content"].append(f"Content-Based Score: {return_score}")

    return return_score, logs_structured, verdict

