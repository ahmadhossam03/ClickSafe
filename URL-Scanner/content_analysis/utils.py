from imports import *
SAFE_DOMAINS = ["amazon.com", "www.amazon.com"]
def is_trusted_domain(url):
    domain = (urlparse(url).hostname or "").lower()
    for safe in SAFE_DOMAINS:
        safe = safe.lower()
        if domain == safe or domain.endswith("." + safe):
            return True
    return False
