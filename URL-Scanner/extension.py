from main import scan_main

def scan_url_for_extension(url: str):
    if not url:
        return "Missing URL", 400

    result = scan_main(url)
    return result["detection"], 200
