from imports import *
from content_analysis.utils import is_trusted_domain
from content_analysis.html_analysis import fetch_html
import jsbeautifier
from pyjsparser import PyJsParser

MAX_JS_LENGTH = 500000
TRUSTED_SCRIPT_DOMAINS = [
    "googletagmanager.com",
    "gstatic.com",
    "googleads.g.doubleclick.net",
    "doubleclick.net",
    "google-analytics.com"
]

MAX_SAFE_INLINE_LENGTH = 10 * 1024


def should_score_script(js_code: str, src_url: str = "") -> bool:
    if src_url and is_trusted_script(src_url):
        return False
    if not src_url and len(js_code) < MAX_SAFE_INLINE_LENGTH:
        return False
    return True


@lru_cache(maxsize=128)
def fetch_javascript(url, html=None):
    try:
        if html is None:
            html = fetch_html(url)
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        scripts = set()
        seen_hashes = set()

        def clean_js(js_text):
            js_text = js_text.strip()
            js_text = re.sub(r'//.*?$|/\*.*?\*/', '', js_text, flags=re.DOTALL | re.MULTILINE)
            js_text = re.sub(r'\s+', ' ', js_text)
            js_text = re.sub(r';+', ';', js_text)
            return js_text

        for script in soup.find_all('script'):
            if not script.has_attr('src') and script.string:
                cleaned = clean_js(script.string)
                content_hash = hashlib.md5(cleaned.encode('utf-8')).hexdigest()
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    scripts.add(cleaned)

        for script in soup.find_all('script', src=True):
            js_url = urljoin(url, script['src'])
            try:
                js_response = requests.get(js_url, timeout=5)
                js_response.raise_for_status()
                js_content = js_response.text
                if len(js_content.encode("utf-8")) > MAX_JS_LENGTH:
                    print(f"Skipping large JS file: {js_url} (>{MAX_JS_LENGTH} bytes)")
                    continue

                cleaned = clean_js(js_content)
                content_hash = hashlib.md5(cleaned.encode('utf-8')).hexdigest()
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    scripts.add(cleaned)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching JS file {js_url}: {e}")
            except Exception as ex:
                print(f"Unexpected error processing JS file {js_url}: {ex}")

        return list(scripts)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching JavaScript: {e}")
        return None


def analyze_javascript(js_scripts, url):
    if not js_scripts:
        return {}, {}

    parser = PyJsParser()
    js_features = {
        "Popup Windows": 1,
        "JavaScript Obfuscation": 1
    }
    js_counts = {
        "Popup Windows": 0,
        "JavaScript Obfuscation": 0
    }

    for script in js_scripts:
        if not should_score_script(script):
            continue

        # Skip modern JavaScript features unsupported by pyjsparser (ECMAScript 5.1)
        if any(keyword in script for keyword in ["=>", "const ", "let ", "class ", "async ", "await "]):
            print("Skipping ES6+ JS due to unsupported syntax.")
            continue

        try:
            pretty_script = jsbeautifier.beautify(script)
            parsed = parser.parse(pretty_script)
            raw = pretty_script.lower()

            # Feature 1: Popup Windows
            if "window.open(" in raw:
                js_features["Popup Windows"] = 3
                js_counts["Popup Windows"] += raw.count("window.open(")


            # Feature 2: Obfuscation Indicators
            obf_indicators = ["activexobject", "createtextfile", "filesystemobject", "fileexists"]
            if any(keyword in raw for keyword in obf_indicators):
                js_features["JavaScript Obfuscation"] = 5
                js_counts["JavaScript Obfuscation"] = sum(raw.count(x) for x in obf_indicators)

        except Exception as e:
            print(f"Error parsing JS: {e}")
            continue

    return js_features, js_counts


def is_trusted_script(src: str) -> bool:
    return any(domain in src for domain in TRUSTED_SCRIPT_DOMAINS)
