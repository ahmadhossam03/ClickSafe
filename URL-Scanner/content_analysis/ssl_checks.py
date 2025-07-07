from imports import *
import certifi

def check_https_from_response(response):
    try:
        if response and response.url.startswith("https://"):
            return 1
        else:
            return 5
    except requests.exceptions.SSLError:
        return 5
    except requests.exceptions.RequestException as e:
        print(f"Error checking HTTPS: {e}")
        return 5

def get_certificate(url):
    """Retrieve SSL certificate details using certifi CA bundle."""
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            return {"SSL Status": "Invalid Hostname"}, 5

        # Use certifi bundle for trusted CAs
        context = ssl.create_default_context(cafile=certifi.where())

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        valid_to = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        valid_from = datetime.strptime(cert.get("notBefore", ""), "%b %d %H:%M:%S %Y %Z")
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        subject = dict(x[0] for x in cert.get("subject", ()))
        now = datetime.utcnow()
        is_valid = valid_to > now

        cert_info = {
            "SSL Status": "Valid Certificate" if is_valid else "Expired Certificate",
            "Issued To": subject.get("commonName", "Unknown"),
            "Issuer": issuer.get("commonName", "Unknown"),
            "Valid From": valid_from.strftime("%Y-%m-%d"),
            "Valid Until": valid_to.strftime("%Y-%m-%d"),
        }

        score = 1 if is_valid else 5
        return cert_info, score

    except (ssl.SSLError, socket.error, socket.timeout) as e:
        return {"SSL Status": "SSL certificate error", "Error": str(e)}, 5
    except Exception as e:
        return {"SSL Status": "SSL validation failed", "Error": str(e)}, 5

def validate_url_certificate(url):
    """Validate SSL certificate of a given URL using certifi."""
    try:
        hostname = urlparse(url).hostname
        context = ssl.create_default_context(cafile=certifi.where())

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        subject = dict(x[0] for x in cert["subject"])
        issuer = dict(x[0] for x in cert["issuer"])
        valid_from = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        valid_to = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        now = datetime.utcnow()

        print(f"Certificate issued to: {subject.get('commonName')}")
        print(f"Issued by: {issuer.get('commonName')}")
        print(f"Valid from: {valid_from} to {valid_to}")

        if valid_to < now:
            print("Certificate has EXPIRED!")
            return False
        else:
            print("Certificate is valid.")
            return True

    except Exception as e:
        print(f"SSL certificate validation error for {url}: {e}")
        return False
