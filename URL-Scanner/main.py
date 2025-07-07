from imports import *
import identifiation
import FeatureEvaluationMethod
import LexicalFeatures
import blackListedFeature
import HostBasedFeature
import ContentBasedFeature
from ContentBasedFeature import content_based_classification
from identifiation import process_url
import json



def deduplicate_logs(logs):
    seen = set()
    deduped = []

    for line in logs:
        # For dictionaries, convert to a hashable form using JSON
        if isinstance(line, dict):
            hashable = json.dumps(line, sort_keys=True)
        else:
            hashable = line

        if hashable not in seen:
            seen.add(hashable)
            deduped.append(line)

    return deduped


def scan_main(url):
    output = {
        "identification": [],
        "blacklist": [],
        "lexical": [],
        "host": [],
        "content": [],
        "general": []
    }



    # Step 1: Get identified/normalized URL
    identified_url = process_url(url, output)

    # Step 2: Run blacklist checks on both raw and identified URLs
    raw_bl_result = blackListedFeature.get_virustotal_report(url, output)
    identified_bl_result = blackListedFeature.get_virustotal_report(identified_url, output)

    # Step 3: Decide which URL to proceed with
    raw_score = float(raw_bl_result["score"])
    identified_score = float(identified_bl_result["score"])

    use_raw = raw_score > identified_score  # Identified wins if scores are equal
    chosen_url = url if use_raw else identified_url
    chosen_bl_result = raw_bl_result if use_raw else identified_bl_result

    # Ensure reason is always present for template rendering
    chosen_bl_result.setdefault("reason", "No reason provided by VirusTotal.")


    # Log only the chosen blacklist result
    output["blacklist"].append(f"Blacklist Score: {chosen_bl_result['score']}")
    output["blacklist"].append(f"➡️ Continuing with {'raw' if use_raw else 'identified'} URL: {chosen_url}")

    output["lexical"].append("Analyzing lexical features")
    lexical_score = LexicalFeatures.print_feature_classification(chosen_url, output)
    output["lexical"].append(f"Lexical Score: {lexical_score}")

    output["host"].append("Analyzing host-based features")
    host_feature_score = HostBasedFeature.extract_host_features(chosen_url, output)
    output["host"].append(f"Host-Based Score: {host_feature_score}")

    output["content"].append("Analyzing content-based features")
    #content_score = ContentBasedFeature.content_based_classification(identified_url, output)
    #content_score = ContentBasedFeature.content_based_classification(identified_url, output)
    content_score, content_logs, content_verdict = ContentBasedFeature.content_based_classification(chosen_url, output)
    output["html_analysis"] = content_logs.get("html_analysis", {})
    output["javascript_analysis"] = content_logs.get("javascript_analysis", {})
    output["security_headers"] = content_logs.get("security_headers", {})
    output["ssl_certificate"] = content_logs.get("ssl_certificate", {})


    output["content"].append(f"Content-Based Score: {content_score}")



    features = {
        "blacklist": float(chosen_bl_result.get("score", 0)),
        "lexical": round(float(lexical_score), 2) if isinstance(lexical_score, (int, float)) else 0,
        "host_based": float(host_feature_score) if isinstance(host_feature_score, (int, float)) else 0,
        "content_based": float(content_score) if isinstance(content_score, (int, float)) else 0   # ✅ ADD THIS LINE
    }


    detection_result = FeatureEvaluationMethod.detect_malicious_url(features)
    # Force override if blacklist status is explicitly "Malicious"
    if chosen_bl_result.get("status", "").lower() == "malicious":
        output["general"].append("Status is malicious")
        detection_result = "Malicious"

    output["general"].append(f"Final Result: {detection_result.upper()}")

    for key in output:
            output[key] = deduplicate_logs(output[key])

    return {
        "url": url,
        "identified_url": identified_url,
        "scores": features,
        "detection": detection_result,
        "logs": output,
        "blacklist": chosen_bl_result,
        "content_verdict": content_verdict
    }


if __name__ == "__main__":
    pass
