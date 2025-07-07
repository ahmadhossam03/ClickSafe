from imports import *

def has_strong_csp(headers):
    """Check if CSP is set and reasonably strong."""
    csp = headers.get("Content-Security-Policy", "").lower()
    if not csp:
        return False  # Missing CSP = weak

    # Acceptable if default-src or script-src is defined and doesn't allow dangerous inline/execution
    dangerous_keywords = ["'unsafe-inline'", "'unsafe-eval'"]
    has_directive = "default-src" in csp or "script-src" in csp
    no_dangerous_content = all(keyword not in csp for keyword in dangerous_keywords)

    return has_directive and no_dangerous_content

def check_security_headers_from_response(response, url):
    """
        Check HTTP security headers related to clickjacking and assign a risk score.

        Returns:
            - header_info: Dict containing header values and human-readable protection status
            - risk_score: int (1 = secure, 3 = suspicious, 5 = vulnerable)
    """
    try:
        if response is None:
            return {"Error": "No response"}, 3
        headers = response.headers
        final_url = response.url

        x_frame_options = headers.get("X-Frame-Options", "").strip()
        csp = headers.get("Content-Security-Policy", "").strip()
        hsts = headers.get("Strict-Transport-Security", "").strip()
        x_content_type = headers.get("X-Content-Type-Options", "").strip()
        referrer_policy = headers.get("Referrer-Policy", "").strip()
        permissions_policy = headers.get("Permissions-Policy", "").strip()
        x_xss_protection = headers.get("X-XSS-Protection", "").strip()
        header_scores = []
        header_info = {}

        # --- X-Frame-Options and CSP (Clickjacking Protection) ---
        if x_frame_options.upper() in ["DENY", "SAMEORIGIN"]:
            clickjacking_score = 1
            clickjacking_status = "Protected (X-Frame-Options)"
        elif "frame-ancestors" in csp.lower():
            clickjacking_score = 1
            clickjacking_status = "Protected (CSP frame-ancestors)"
        elif x_frame_options or csp:
            clickjacking_score = 3
            clickjacking_status = "Partial Protection (non-standard value)"
        else:
            clickjacking_score = 5
            clickjacking_status = "No Clickjacking Protection"

        # Check for HSTS
        header_scores.append(clickjacking_score)
        header_info["Frame Protection"] = clickjacking_status
        header_info["X-Frame-Options"] = x_frame_options or "Not Set"
        header_info["Content-Security-Policy"] = csp or "Not Set"
        # --- HSTS ---
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            if hsts:
                hsts_score = 1
                hsts_status = "Set"
            else:
                hsts_score = 2
                hsts_status = "Not Set (HTTPS, likely preloaded)"
        else:
            hsts_score = 3
            hsts_status = "Not Set (HTTP only)"
        header_scores.append(hsts_score)
        header_info["HSTS Protection"] = hsts_status
        header_info["Strict-Transport-Security"] = hsts or "Not Set"

        # --- X-Content-Type-Options ---
        if x_content_type.lower() == "nosniff":
            content_type_score = 1
            content_type_status = "nosniff set"
        else:
            content_type_score = 3
            content_type_status = "Missing or misconfigured"
        header_scores.append(content_type_score)
        header_info["Content-Type Protection"] = content_type_status
        header_info["X-Content-Type-Options"] = x_content_type or "Not Set"

        # --- Referrer-Policy ---
        if referrer_policy:
            referrer_score = 1
            referrer_status = "Set"
        elif has_strong_csp(headers):
            referrer_score = 1
            referrer_status = "CSP compensates for missing Referrer-Policy"
        else:
            # Relax penalty if HTTPS and HSTS are present
            if parsed_url.scheme == "https" and hsts:
                referrer_score = 0.5
                referrer_status = "Missing but mitigated by HTTPS + HSTS"
            else:
                referrer_score = 2
                referrer_status = "Missing"

        header_scores.append(referrer_score)
        header_info["Referrer Protection"] = referrer_status
        header_info["Referrer-Policy"] = referrer_policy or "Not Set"

        # --- Permissions-Policy (new privacy header) ---
        if permissions_policy:
            permissions_score = 1
            permissions_status = "Set"
        else:
            permissions_score = 2
            permissions_status = "Missing"
        header_scores.append(permissions_score)
        header_info["Permissions Policy"] = permissions_status
        header_info["Permissions-Policy"] = permissions_policy or "Not Set"

        # --- X-XSS-Protection (legacy) ---
        if x_xss_protection and x_xss_protection.startswith("1"):
            xss_score = 1
            xss_status = "Enabled (legacy)"
        elif x_xss_protection == "0":
            if "Content-Security-Policy" in headers and "script-src" in headers["Content-Security-Policy"]:
                xss_score = 1
                xss_status = "Disabled intentionally, CSP present"
            else:
                xss_score = 3
                xss_status = "Disabled without strong CSP"
        elif x_xss_protection:
            xss_score = 3
            xss_status = "Misconfigured"
        else:
            xss_score = 3
            xss_status = "Not Set"

        header_scores.append(xss_score)
        header_info["XSS Protection"] = xss_status
        header_info["X-XSS-Protection"] = x_xss_protection or "Not Set"

        # Final average score
        average_header_score = round(sum(header_scores) / len(header_scores), 2)
        #if is_trusted_domain(url):
            # Soften penalty on safe domains missing HSTS/CSP
            #average_header_score = min(average_header_score, 1.2)

        header_info["Average Header Risk Score"] = average_header_score
        if average_header_score > 1.5 and (
            x_xss_protection == "0" and not hsts and not csp and x_frame_options
        ):
            print("Likely intentional missing headers on modern site — lowering penalty")
            #average_header_score = round(average_header_score * 0.75, 2)
            average_header_score = round(min(average_header_score * 0.75, 1.25), 2)
            if average_header_score < 1:
                average_header_score = 1
            header_info["Average Header Risk Score"] = average_header_score


        if x_frame_options and x_frame_options.lower() in ["sameorigin", "deny"] \
            and x_xss_protection == "0" \
            and not csp and not hsts:

            print("Modern site using preload and browser defaults — applying soft trust bonus")
            average_header_score = round(min(average_header_score * 0.7, 1.1), 2)

        return header_info, average_header_score

    except requests.exceptions.RequestException as e:
        return {"Error": f"Failed to fetch headers: {e}"}, 3  # Treat network errors as medium risk
    except Exception as ex:
        return {"Error": f"Unexpected error: {ex}"}, 3  # Handle unexpected errors gracefully