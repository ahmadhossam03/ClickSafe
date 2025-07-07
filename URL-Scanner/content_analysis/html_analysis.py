import re
from typing import Dict, Tuple
from bs4 import BeautifulSoup
from imports import *
from urllib.parse import urlparse
from content_analysis.utils import is_trusted_domain
from playwright.sync_api import sync_playwright


def fetch_html(url):
    """
    Uses Playwright to fetch full HTML content of a webpage using a headless browser.
    Returns the HTML as a string.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            page.goto(url, timeout=10000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"Error fetching HTML using browser: {e}")
        return None


def counting_occurrences(html, patterns):
    """
    Count regex-based occurrences of specified features in the HTML string.
    """
    counts = {}
    if not isinstance(html, str):
        for feature in patterns:
            counts[feature] = 0
        return counts

    for feature, pattern in patterns.items():
        try:
            counts[feature] = len(re.findall(pattern, html, re.IGNORECASE))
        except Exception:
            counts[feature] = 0
    return counts


def detect_iframes(html_content):
    """Detects suspicious iframe behavior, prioritizing clickjacking signs over benign uses."""
    if not html_content:
        return 1, "No HTML content provided for iframe analysis.", []

    try:
        soup = BeautifulSoup(html_content, "lxml")
        suspicious_iframe_count = 0
        max_nesting_depth = 0
        suspicious_snippets = []
        RECURSION_LIMIT = 20
        total_flags = 0

        def get_iframe_depth(tag, depth=0):
            nonlocal max_nesting_depth
            if depth > RECURSION_LIMIT:
                return
            if tag.name == "iframe":
                max_nesting_depth = max(max_nesting_depth, depth)
            for child in tag.find_all("iframe", recursive=False):
                get_iframe_depth(child, depth + 1)

        for iframe in soup.find_all("iframe"):
            flags = []
            high_risk = False
            style = iframe.get("style", "").lower().replace(" ", "")

            width_val, height_val = None, None
            try:
                width_val = int(re.sub(r"[^\d]", "", iframe.get("width", "")))
                height_val = int(re.sub(r"[^\d]", "", iframe.get("height", "")))
            except:
                pass

            # === Low-Risk Flags (No high score) ===
            if "display:none" in style or "visibility:hidden" in style or "opacity:0" in style:
                flags.append("Hidden via style")
            if width_val is not None and width_val <= 5:
                flags.append("Tiny width iframe")
            if height_val is not None and height_val <= 5:
                flags.append("Tiny height iframe")

            # === High-Risk Clickjacking Indicators ===
            # === High-Risk Clickjacking Indicators ===

            # Confirmed malicious if ALL 3 styles are present
            if (
                "position:absolute" in style
                and "z-index" in style
                and "pointer-events:none" in style
            ):
                flags.append("Confirmed malicious clickjacking overlay (absolute + z-index + no pointer events)")
                high_risk = True

            # Suspicious, but not confirmed — if at least 2 risky styles are present
            elif sum(
                indicator in style
                for indicator in ["position:absolute", "z-index", "pointer-events:none"]
            ) >= 2:
                flags.append("Likely clickjacking overlay (2 risky styles detected)")
                high_risk = True

            # Suspicious, but weaker indication — only 1 risky style
            elif (
                "position:absolute" in style
                or "z-index" in style
                or "pointer-events:none" in style
            ):
                flags.append("Weak clickjacking indicator (1 risky style)")

            if iframe.get("scrolling", "").lower() == "no":
                flags.append("Scrollbar Hidden")
            if iframe.get("frameborder", "") == "0":
                flags.append("No Border")
            if iframe.get("width", "") == "100%" and iframe.get("height", "") == "100%":
                flags.append("Full Page Overlay")
                high_risk = True


            # Only count iframes as suspicious if they include high-risk indicators
            if high_risk:
                suspicious_iframe_count += 1
                total_flags += len(flags)
                suspicious_snippets.append({
                    "iframe": str(iframe)[:300],
                    "flags": flags
                })

        get_iframe_depth(soup)

        score = 1 + suspicious_iframe_count + (0.5 * total_flags)
        if max_nesting_depth >= 2:
            score += max_nesting_depth

        final_score = min(round(score), 5)

        verdict = "Suspicious"
        for snippet in suspicious_snippets:
            if any("Confirmed malicious" in f for f in snippet["flags"]):
                verdict = "Malicious"
                break

        if final_score == 1:
            message = "No suspicious iframe behavior detected."
        else:
            message = f"Detected {suspicious_iframe_count} suspicious iframe(s), {total_flags} clickjacking-related tricks."
            if max_nesting_depth >= 2:
                message += f" Nested iframes (depth {max_nesting_depth}) detected."
            message += f" Verdict: {verdict}"


        return final_score, message, suspicious_snippets

    except Exception as e:
        print(f"Error during iframe detection: {e}")
        return 1, "Error during iframe analysis.", []



def analyze_content(html, url) -> Tuple[Dict[str, float], Dict[str, int]]:
    """
    Analyzes content features in HTML such as:
    - Iframes
    - mailto links
    - suspicious JavaScript
    - insecure forms
    """
    if not html:
        return {}, {}

    try:
        soup = BeautifulSoup(html, 'lxml')

        # Feature pattern counts
        feature_patterns = {
            "Iframe": r"<iframe\b",
            #"JavaScript Functions": r"\b(eval|exec|unescape)\s*\(",
            #"DOM Functions": r"\b(appendChild|createElement)\s*\(",
            #"JavaScript Obfuscation": r"\b(ActiveXObject|CreateObject|FileSystemObject|String\.fromCharCode)\s*\(",
        }
        counts = counting_occurrences(html, feature_patterns)
        features = {k: 1 for k in counts}

        # Mailto links (only real anchor tags)
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        counts["Mailto"] = len(mailto_links)
        features["Mailto"] = 1  # Keep risk score low for mailto

        # Insecure form handling
        insecure_forms = 0
        for form in soup.find_all('form'):
            action = form.get('action', '').strip()
            if action.startswith('http://') or (
                urlparse(action).hostname and urlparse(action).hostname != urlparse(url).hostname
            ):
                insecure_forms += 1
        counts["Insecure Form"] = insecure_forms
        features["Insecure Form"] = 1 if insecure_forms == 0 else (5 if not is_trusted_domain(url) else 3)

        # Redirect status
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
            status_code = resp.status_code
            if 300 <= status_code < 400:
                features["Redirect Status"] = 3
            else:
                features["Redirect Status"] = 1
            counts["Redirect Status"] = status_code
        except requests.RequestException:
            features["Redirect Status"] = 3
            counts["Redirect Status"] = 0

        return features, counts

    except Exception as e:
        print(f"An unexpected error occurred during content analysis: {e}")
        return {}, {}
