from flask import Flask, request, render_template
from main import scan_main  # ✅ This is your real logic function
from flask import Flask, request
from flask_cors import CORS, cross_origin
from extension import scan_url_for_extension
#ELGDEDED

from flask_cors import CORS, cross_origin

# Add this after creating your Flask app
app = Flask("URL Scanner")
CORS(app)  # This enables CORS for all routes


def deduplicate_logs(logs):
    seen = set()
    unique_logs = []
    for log in logs:
        if log not in seen:
            unique_logs.append(log)
            seen.add(log)
    return unique_logs

app.jinja_env.filters['dedup'] = deduplicate_logs

# ✅ Renamed this view function so it doesn't conflict with the imported `scan_main`
@app.route("/scan", methods=["GET", "POST"])
@cross_origin()
def handle_scan():
    # Get URL from query string or form data
    if request.method == "POST":
        url = request.form.get("url")
    else:
        url = request.args.get("url")
    print(f"Received URL: {url}")
    
    # Call the real scan_main function with the URL
    result = scan_main(url)
    #print(f"Scan result: {result}")

    # Render the result in the HTML template
    return render_template("result.html", result=result)


@app.route("/api/scan_url_json", methods=["GET", "POST"])
@cross_origin()
def scan_json():
    if request.method == "POST":
        url = request.form.get("url")
    else:
        url = request.args.get("url")
    return scan_url_for_extension(url)

if __name__ == "__main__":
    app.run(port=5001, debug=True)


