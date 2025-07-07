from imports import *
import math
from ipwhois import IPWhois
import socket
import dns.resolver
from urllib.parse import urlparse
from identifiation import process_url



# Constants for API Keys (Replace with actual API keys)
OPR_API_KEY = "kwokcww4g4s44k4ggksokcg088og8g88k4wcsg0c"
OPR_URL = "https://openpagerank.com/api/v1.0/getPageRank"

HOST_FEATURE_EXPLANATIONS = {
    "Global Rank": "Global traffic rank of the domain. Lower rank (closer to 1) is considered more trustworthy.",
    "Subdomain Count": "Number of subdomain levels in the domain name. More levels may indicate suspicious structure.",
    "Typosquatting": "Checks if the domain closely resembles popular domains (e.g., 'gooogle.com').",
    "ASN Number": "Autonomous System Number identifying the hosting network. Some ASNs are commonly associated with abuse."
}



HOST_FEATURE_WEIGHTS = {
    "Global Rank": 0.3,
    "DNS Records": 0.2,
    "Subdomain Count": 0.2,
    "Typosquatting": 0.2,
    "ASN Number": 0.1
}
shady_asns = {
        "AS202425",  # Host Sailor
        "AS9009",    # M247 Ltd (abuse frequently reported)
        "AS12389",   # Rostelecom (Russia - high-risk APT activity)
        "AS20473",   # Choopa / Vultr (often used in phishing kits)
        "AS14061",   # DigitalOcean (neutral but often abused by attackers)
        "AS53667",   # FranTech Solutions (used by VPNs/Tor exit nodes)
        "AS20454",   # SS8 Networks / ASN Hosting
        "AS58224",   # IPXO (abused reassigned IPs)
        "AS29073",   # Quasi Networks LTD (bulletproof hosting)
        "AS60068",   # Datacamp Limited (VPN abuse)
        "AS210644",  # Njalla (known for privacy + dark web hosting)
        "AS29182",   # ISPA Network (frequent phishing kit origin)
        "AS48635",   # HostFly (spam and C2 operations)
        "AS49981",   # WorldStream B.V. (associated with malware infra)
        "AS210630",  # Boreus GmbH (recent botnet infra)
        }

shady_countries = {
    "RU",  # Russia
    "CN",  # China
    "IR",  # Iran
    "KP"  # North Korea
}

POPULAR_DOMAINS = ["google.com", "facebook.com", "youtube.com", "amazon.com", "microsoft.com"]
# WHOIS and date calculations
def days_since(date_str):
    try:
        return (datetime.datetime.today() - datetime.datetime.fromisoformat(date_str)).days
    except:
        return None


def is_ip_address(url):
    try:
        parts = url.split(".")
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


# Function to clean the domain
def clean_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else url
    return domain.replace("www.", "")


# Fetch Open Page Rank
def fetch_opr_rank(url):
    try:
        cleaned_url = clean_domain(url)
        headers = {"API-OPR": OPR_API_KEY}
        params = {"domains[]": cleaned_url}
        response = requests.get(OPR_URL, headers=headers, params=params, timeout=30)

        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # Handle OpenPageRank error if present
            if "ErrorMessage" in data:
                error_msg = data["ErrorMessage"].get("msg", "Unknown error")
                print(f"OPR API Error: {error_msg}")
                return None

            if data.get("response"): # 444444444444444444444444444444444444444444
                return int(data["response"][0].get("rank", 0)) # 4444444444444444444444444444444444444444444

            print("Full API Response:", data)  # Debugging output

            # Extract relevant data
            if "response" in data and isinstance(data["response"], list) and len(data["response"]) > 0:
                domain_data = data["response"][0]  # Assuming first entry is the required domain

                # Extract and store data in separate variables
                # all can be removed except rank ?????????????????????????????????????????????????
                page_rank_integer = int(domain_data.get("page_rank_integer", 0))  # Convert to int
                page_rank_decimal = float(domain_data.get("page_rank_decimal", 0.0))  # Convert to float
                rank = int(domain_data.get("rank", 0)) if domain_data.get("rank") and domain_data["rank"].isdigit() else 0  # Convert to int
                domain = domain_data.get("domain", "")
                status_code = domain_data.get("status_code", "")
                error_message = domain_data.get("error_message", "")

                # Print extracted values
                print(f"Page Rank Integer: {page_rank_integer}")
                print(f"Page Rank Decimal: {page_rank_decimal}")
                print(f"Rank: {rank}")
                print(f"Domain: {domain}")
                print(f"Status Code: {status_code}")
                print(f"Error Message: {error_message}")

                return rank  # Return rank for use in the feature extraction

            else:
                print("Unexpected API response format:", data)
        else:
            print(f"API request failed with status code {response.status_code}: {response.text}")

    except requests.exceptions.Timeout:
        print("Error: API request timed out.")
    except requests.exceptions.ConnectionError:
        print("Error: Network issue. Check your internet connection.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return "N/A"


def get_dns_records(domain: str) -> dict:
    try:
        # Clean domain if full URL is passed
        parsed = urlparse(domain)
        clean_domain = parsed.netloc if parsed.netloc else parsed.path
        clean_domain = clean_domain.replace("www.", "")

        # DNS Resolver setup
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google DNS
        resolver.timeout = 5
        resolver.lifetime = 10

        record_types = ["A", "MX", "TXT"]
        results = {}
        total_records = 0

        for rtype in record_types:
            try:
                answer = resolver.resolve(clean_domain, rtype)
                records = [r.to_text() for r in answer]
                results[rtype] = {
                    "count": len(records),
                    "records": records,
                    "status": "success"
                }
                total_records += len(records)

            except dns.resolver.NoAnswer:
                results[rtype] = {"count": 0, "records": [], "status": "no_answer"}
            except dns.resolver.NXDOMAIN:
                return {
                    "success": False,
                    "error": f"Domain '{clean_domain}' does not exist (NXDOMAIN).",
                    "total_records": 0,
                    "records": {}
                }
            except dns.resolver.Timeout:
                results[rtype] = {"count": 0, "records": [], "status": "timeout"}
            except Exception as e:
                results[rtype] = {"count": 0, "records": [], "status": f"error: {str(e)}"}

        return {
            "success": True,
            "domain": clean_domain,
            "total_records": total_records,
            "records": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"General DNS error: {e}",
            "total_records": 0,
            "records": {}
        }


def get_subdomain_count(domain):
    try:
        parts = domain.split(".")
        return len(parts) - 2 if len(parts) > 2 else 0
    except:
        return 0

def detect_typosquatting(domain):
    try:
        matches = difflib.get_close_matches(domain, POPULAR_DOMAINS, n=1, cutoff=0.8)
        return 1 if matches else 0
    except:
        return 0

def get_asn_number(domain):
    try:
        ip = socket.gethostbyname(domain)
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        asn = res.get("asn")
        return asn if asn else "Unknown"
    except Exception as e:
        print(f"ASN lookup failed for {domain}: {e}")
        return "Unknown"

def get_ip_country(domain):
    try:
        ip = socket.gethostbyname(domain)
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        country = res.ge
        country = res.get("network", {}).get("country")
        return country if country else "Unknown"
    except Exception as e:
        print(f"IP country lookup failed for {domain}: {e}")
        return "Unknown"

# #########################################################
def calculate_feature_score(feature, value):
    try:
        value = float(value)  # or int(value) if you're sure it's always a whole number
    except (ValueError, TypeError):
        return 5  # Return max risk if the value is not numeric


    if value is None:
        return 3  # Not 0: this avoids giving it artificially low score for missing values

    if feature == "Global Rank":
        return 1 if value and value <= 10000 else 3 if value and value <= 50000 else 5
    #elif feature == "Total Visits":
        #return 1 if value >= 1_000_000 else 3 if 50_000 < value < 1_000_000 else 5
    elif feature == "Subdomain Count":
        return 1 if value <= 1 else 3 if value <= 3 else 5
    elif feature == "Typosquatting":
        return 5 if value else 1
    elif feature == "ASN Number":
        return 5 if value in shady_asns else 1
    return 3



def calculate_weighted_score(feature_values: Dict[str, any]) -> float:
    weighted_sum = 0
    total_weight = 0

    print("\nWeighted Host Score Calculation:")
    for feature, value in feature_values.items():
        score = calculate_feature_score(feature, value)
        weight = HOST_FEATURE_WEIGHTS.get(feature, 0)

        print(f"Feature: {feature} | Value: {value} | Score: {score} | Weight: {weight}")

        weighted_sum += score * weight
        total_weight += weight

    final_score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
    print(f"Final Weighted Host Score: {final_score}")
    return final_score


def extract_host_features(url, output):
    if is_ip_address(url):
        output["host"].append("Error: Cannot fetch WHOIS data for IP addresses.")
        return -1

    # Fetch WHOIS data and OPR rank
    domain = clean_domain(url)

    opr_rank = fetch_opr_rank(url)
    subdomain_count = get_subdomain_count(domain)
    typosquatting = detect_typosquatting(domain)
    asn_number = get_asn_number(domain)
    ip_country = get_ip_country(domain)




    # Prepare feature values
    feature_values = {
        "Global Rank": opr_rank,
        "Subdomain Count": subdomain_count,
        "Typosquatting": typosquatting,
        "ASN Number": asn_number
    }

    #output["host"].append("\nFeature Scores:")
    for feature, value in feature_values.items():
        score = calculate_feature_score(feature, value)
        explanation = HOST_FEATURE_EXPLANATIONS.get(feature, "No explanation available.")
        output["host"].append(f"{feature}: {score} | {explanation}")


    final_score = calculate_weighted_score(feature_values)
    if asn_number in shady_asns:
        output["host"].append(f"Warning: ASN {asn_number} is associated with suspicious activity.")

    if ip_country in shady_countries:
        output["host"].append(f"Warning: IP is located in a high-risk country ({ip_country}).")


    return final_score
