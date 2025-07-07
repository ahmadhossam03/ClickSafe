from imports import *
import re
import requests
import tldextract
from urllib.parse import urlparse, parse_qs, unquote, urljoin

SHORTENERS = [
    "bit.ly", "t.co", "goo.gl", "tinyurl.com", "ow.ly", "is.gd", "buff.ly",
    "adf.ly", "rebrand.ly", "shorte.st", "cut.ly"
]

DANGEROUS_EXTENSIONS = [".exe", ".apk", ".zip", ".rar", ".bat", ".cmd", ".js", ".msi"]
REDIRECT_KEYS = ["url", "u", "redirect", "dest", "target", "next", "redir", "rurl", "to", "link"]

def log_message(message, output=None):
    print(message)
    if output is not None:
        output.append(message)

def has_dangerous_extension(url):
    return any(url.lower().endswith(ext) for ext in DANGEROUS_EXTENSIONS)

def is_shortened_url(url):
    extracted_domain = tldextract.extract(url).registered_domain
    return extracted_domain in SHORTENERS

def resolve_url(url, output=None):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        redirection_chain = [resp.url for resp in response.history]
        final_url = response.url

        if redirection_chain:
            log_message("Redirections detected:", output)
            for i, r_url in enumerate(redirection_chain):
                log_message(f"  {i+1}. {r_url}", output)
            log_message(f"Final URL after redirections: {final_url}", output)

        return final_url, redirection_chain

    except requests.RequestException:
        log_message("Failed to resolve URL — using original.", output)
        return url, []

def detect_obfuscation(url):
    obfuscation_flags = {
        "contains_ip": bool(re.match(r"https?://\d{1,3}(?:\.\d{1,3}){3}", url)),
        "contains_suspicious_keywords": any(keyword in url.lower() for keyword in ["secure", "verify", "update", "account", "login", "bank"]),
        "lengthy_domain": len(tldextract.extract(url).domain) > 20
    }
    return obfuscation_flags

def extract_redirect_target(url, output):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Step 1: Clean up malformed query
    if '?' not in url and '&' in url:
        # Fix malformed URL like `http://example.com/&url=http://...`
        url = url.replace('&', '?', 1)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

    # Step 2: Check common redirection parameters
    for key in REDIRECT_KEYS:
        if key in query:
            extracted = unquote(query[key][0])
            if extracted.startswith("http"):
                log_message(f"Redirect parameter '{key}' found ➜ Extracted URL: {extracted}", output)
                return extracted

    # Step 3: Regex fallback for embedded URL
    regex_urls = re.findall(r"https?://[^\s\"'>]+", url)
    for candidate in regex_urls:
        if candidate != url and tldextract.extract(candidate).domain:
            log_message(f"Embedded URL detected via regex ➜ Extracted URL: {candidate}", output)
            return candidate

    return url

def process_url(url, output):
    log_message(f"\nProcessing URL: {url}", output["identification"])
    log_message(f"Initial URL: {url}", output["identification"])

    visited = set()
    current_url = url

    # Step 1: Recursively extract embedded redirect URLs (max depth 3)
    for _ in range(3):
        if current_url in visited:
            break
        visited.add(current_url)
        extracted = extract_redirect_target(current_url, output["identification"])
        if extracted != current_url:
            log_message(f"Redirect detected. Updating URL: {extracted}", output["identification"])
            current_url = extracted
        else:
            break

    # Step 2: Check for dangerous extension
    if has_dangerous_extension(current_url):
        log_message("Warning: Dangerous file extension detected!", output["identification"])

    # Step 3: Handle shorteners
    if is_shortened_url(current_url):
        log_message("Shortened URL detected. Attempting to expand...", output["identification"])

    # Step 4: Follow real HTTP redirects
    final_url, redirections = resolve_url(current_url, output["identification"])

    # Step 5: Recursively check redirect params again after HTTP redirection
    for _ in range(2):
        new_extracted = extract_redirect_target(final_url, output["identification"])
        if new_extracted != final_url:
            log_message(f"Redirect detected in final URL ➜ Switching to: {new_extracted}", output["identification"])
            final_url, _ = resolve_url(new_extracted, output["identification"])
        else:
            break

    # Step 6: Obfuscation
    obfuscation_results = detect_obfuscation(final_url)
    if any(obfuscation_results.values()):
        log_message("Obfuscation signs detected:", output["identification"])
        for key, value in obfuscation_results.items():
            if value:
                log_message(f"  - {key.replace('_', ' ').title()}", output["identification"])

    log_message("\nURL Analysis Completed!", output["identification"])
    log_message(f"Final URL: {final_url}", output["identification"])
    log_message(f"Normalized URL: {final_url}", output["identification"])

    return final_url
