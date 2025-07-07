from imports import *
verdict=0


def get_scan_date(scan_res):
    for line in scan_res.splitlines():
        if "last_analysis_date" in line:
            match = re.search(r'(\d+)', line)  # Extract first number found
            if match:
                timestamp = int(match.group(0))
                return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return "No scan date found"







api_key= "7ab5f0228475a1cc39da09508c0b8b3b49345deb5d80e35154338a67ccca7969"
api_key_2="6e17a38f13b1a9ed9b61b3f61d8b7458594030fccb5f0ad0399f08dbe3d61bf1"
api_key_3="21b52c3be1353e500e1c75c4ec46a0180a3db2416bdcc7222729eb6fb7fee22a"
def get_file_hash(file_path):
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def scan_url_submission(target_url, api_key):
    """Submit a URL to VirusTotal for scanning and return the results"""
    import base64
    import time
    
    # First, submit the URL for scanning
    submit_url = "https://www.virustotal.com/api/v3/urls"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "x-apikey": api_key
    }
    
    data = {
        "url": target_url
    }
    
    # Submit URL for scanning
    response = requests.post(submit_url, headers=headers, data=data)
    
    if response.status_code != 200:
        return f"Error submitting URL: {response.text}"
    
    try:
        submission_result = response.json()
        url_id = submission_result.get('data', {}).get('id')
        
        if not url_id:
            return "Error: Could not get URL ID from submission"
        
        # Wait a moment for analysis to begin
        time.sleep(2)
        
        # Get the analysis results
        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{url_id}"
        analysis_headers = {
            "accept": "application/json",
            "x-apikey": api_key
        }
        
        analysis_response = requests.get(analysis_url, headers=analysis_headers)
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            
            # Extract malicious count from stats
            stats = result.get('data', {}).get('attributes', {}).get('stats', {})
            malicious_count = stats.get('malicious', 0)
            suspicious_count = stats.get('suspicious', 0)
            
            # Return safe if no malicious or suspicious detections, otherwise unsafe
            if malicious_count == 0 and suspicious_count == 0:
                return "safe"
            else:
                return "unsafe"
        else:
            return "No Scan"  # Default to unsafe if scan fails

    except json.JSONDecodeError:
        return "No Scan"  # Default to unsafe on error
    except Exception as e:
        return "No Scan"  # Default to unsafe on error


from typing import Optional, Dict, Any

def get_abuseipdb_report(ip_address: str, api_key: str, max_age_days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Checks an IP address against the AbuseIPDB database.

    Args:
        ip_address: The IP address to check.
        api_key: Your AbuseIPDB API key.
        max_age_days: The max age in days of reports to consider.

    Returns:
        A dictionary with the API response, or None on error.
    """
    url = 'https://api.abuseipdb.com/api/v2/check'
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    params = {
        'ipAddress': ip_address,
        'maxAgeInDays': max_age_days,
        'verbose': True  # Use 'verbose' to get recent reports
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Will raise an exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying AbuseIPDB: {e}")
        return None
ip_api_key="b2b301e089f1acdb99ebb34a229b6835e0706c7f65cd5c91fd8227b838dc0be6bdbbb41c9dda1c7f"







def scan_file(file, api_key):
    file_hash = get_file_hash(file)  # Ensure we have the correct hash format
    result = ""
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }
    response = requests.get(url, headers=headers)

    try:
        output = response.json()  # Ensure we have a valid JSON response
        # Extract only the total_votes section
        total_votes = output.get('data', {}).get('attributes', {}).get('total_votes', {})
        if total_votes:
            # Format as requested: total_votes : "harmless" -> 16, "malicious"->2
            harmless = total_votes.get('harmless', 0)
            malicious = total_votes.get('malicious', 0)
            if malicious > 0:
                formatted_output=f'VirusTotal Verdict: Malicious'
            else:
                formatted_output=f'VirusTotal Verdict: Safe'
            result += formatted_output
            result += "\n-------------------------------\n"
            return result

        else:
            result += "No total_votes data found"
            result += "\n-------------------------------\n"
            return result

    except json.JSONDecodeError:
        return "Error: Invalid JSON response from VirusTotal."

def get_scan_date(scan_res):
    for line in scan_res.splitlines():
        if "last_analysis_date" in line:
            match = re.search(r'(\d+)', line)  # Extract first number found
            if match:
                timestamp = int(match.group(0))
                return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return "No scan date found"

def scan_file_sandbox(file_hash, api_key):
    result = ""
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }
    response = requests.get(url, headers=headers)

    try:
        output = response.json()  # Ensure we have a valid JSON response
        
        # Extract only the total_votes section
        total_votes = output.get('data', {}).get('attributes', {}).get('total_votes', {})
        
        if total_votes:
            # Format as requested: total_votes : "harmless" -> 16, "malicious"->2
            harmless = total_votes.get('harmless', 0)
            malicious = total_votes.get('malicious', 0)
            formatted_output = f'Votes : "Malicious"-> {malicious}'
            result += formatted_output
            return result

        else:
            result += "No total_votes data found"
            return result

    except json.JSONDecodeError:
        return "Error: Invalid JSON response from VirusTotal."


def main(ip,api_key):
    ABUSEIPDB_KEY = api_key
    if not ABUSEIPDB_KEY:
        return "No Scan"
    else:
        # Example with an IP often reported for abuse
        ip_to_check = ip
        report_data = get_abuseipdb_report(ip_to_check, ABUSEIPDB_KEY)

        if report_data and 'data' in report_data:
            data = report_data['data']
            score = data.get('abuseConfidenceScore')
            if score > 50:
                return "Malicious"
            elif score > 0:
                return "Suspicious"
            else:
                return "Safe"
            
#file=r"D:\Games\Power Rangers - Super Legends\GameLauncher.exe"
#file=r"D:\Games\Power Rangers - Super Legends\GameLauncher.exe"
#file=r"D:\Downloads (Exten)\SysinternalsSuite\procexp.exe"
#print(scan_file(file, api_key))