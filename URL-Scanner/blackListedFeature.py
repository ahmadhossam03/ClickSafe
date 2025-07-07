from imports import *
import base64
import requests
import time

# Replace with your actual VirusTotal API key
API_KEY = "5960d9d01e62ec12b035ac7c21ac7e4bd903a922c077dc87d705c7efebffa8c7"

def encode_url(url):
    """Encodes a URL in base64 (without padding) for VirusTotal API requests."""
    try:
        url_bytes = url.encode("utf-8")
        base64_bytes = base64.urlsafe_b64encode(url_bytes)
        return base64_bytes.decode("utf-8").strip("=")  # Remove padding "="
    except Exception as e:
        print(f"[ERROR] Failed to encode URL: {e}")
        return None

def submit_url_to_virustotal(url):
    """Submit a URL to VirusTotal for scanning."""
    vt_url = "https://www.virustotal.com/api/v3/urls"
    headers = {"x-apikey": API_KEY, "Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(vt_url, headers=headers, data={"url": url})
    try:
        json_data = response.json()
    except Exception:
        json_data = {"error": response.text}

    if response.status_code == 200:
        return response.json()["data"]["id"]  # Return analysis ID
    else:
        print(f"[ERROR] Failed to submit URL. Response: {response.json()}")
        return None

def get_virustotal_report(url, output, retries=1):
    """
    Check if a URL is flagged as malicious in VirusTotal's database.
    """
    try:
        encoded_url = encode_url(url)
        if not encoded_url:
            output.append("[ERROR] Failed to encode URL for VirusTotal.")
            return {
                "score": -1,
                "phishing": 0,
                "malicious": 0,
                "suspicious": 0,
                "status": "Error"
            }
        report_url = f"https://www.virustotal.com/api/v3/urls/{encoded_url}"
        headers = {"x-apikey": API_KEY}

        response = requests.get(report_url, headers=headers)

        if response.status_code == 200:
            report_data = response.json()
            if "data" in report_data and "attributes" in report_data["data"]:
                stats = report_data["data"]["attributes"]["last_analysis_stats"]

                # Get all three counts
                phishing_count = stats.get("phishing", 0)
                malicious_count = stats.get("malicious", 0)
                suspicious_count = stats.get("suspicious", 0)

                # Default values
                status = "Safe"
                score = 1
                reason = "No detections found."

                # Decision logic with reason
                if phishing_count == 0 and malicious_count == 0 and suspicious_count == 0:
                    status = "Safe"
                    score = 1
                    reason = "No detections found in VirusTotal."
                elif malicious_count >= suspicious_count and malicious_count > 0:
                    status = "Malicious"
                    score = 5
                    reason = f"Flagged as malicious by {malicious_count} engine(s)."
                elif suspicious_count > malicious_count:
                    status = "Suspicious"
                    score = 3
                    if phishing_count > 0:
                        reason = f"Flagged as phishing by {phishing_count} engine(s)."
                    else:
                        reason = f"Flagged as suspicious by {suspicious_count} engine(s)."
                else:
                    status = "Suspicious"
                    score = 3
                    reason = f"Flagged as suspicious or phishing by {suspicious_count} engine(s)."

                # Log to report
                output["blacklist"].append("VirusTotal URL Scan Report")
                output["blacklist"].append(f"Phishing Detections: {phishing_count}")
                output["blacklist"].append(f"Malicious Detections: {malicious_count}")
                output["blacklist"].append(f"Suspicious Detections: {suspicious_count}")
                output["blacklist"].append(f"Final Status: {status}")
                output["blacklist"].append(f"🧾 Reason: {reason}")

                # Return all results
                return {
                    "score": score,
                    "phishing": phishing_count,
                    "malicious": malicious_count,
                    "suspicious": suspicious_count,
                    "status": status,
                    "reason": reason  # Include this for full report access
                }


        elif response.status_code == 404:
            output["blacklist"].append("[INFO] No previous scan found. Submitting for analysis...")
            if retries <= 0:
                output["blacklist"].append("[ERROR] Max retries reached. Could not get report.")
                return {"score": -1, "phishing": 0, "malicious": 0, "suspicious": 0, "status": "Error"}
            analysis_id = submit_url_to_virustotal(url)
            if analysis_id:
                output["blacklist"].append("[INFO] Waiting for analysis results...")
                time.sleep(15)  # Wait before retrying
                return get_virustotal_report(url, output, retries=retries - 1)
            else:
                return {"score": -1, "phishing": 0, "malicious": 0, "suspicious": 0, "status": "Error"}

        else:
            output["blacklist"].append(f"[ERROR] Unexpected response: {response.status_code}")
            return {"score": -1, "phishing": 0, "malicious": 0, "suspicious": 0, "status": "Error"}
    except Exception as e:
        output["blacklist"].append(f"[FATAL ERROR] Unexpected failure in VirusTotal scan: {e}")
        return {"score": -1, "phishing": 0, "malicious": 0, "suspicious": 0, "status": "Error"}