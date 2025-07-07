from flask import Flask, request
from flask_cors import CORS, cross_origin
from extension import scan_url_for_extension

app = Flask("ClickSafe Extension API")
CORS(app)

@app.route("/api/scan_url_json", methods=["GET"])
@cross_origin()
def scan_json():
    url = request.args.get("url")
    return scan_url_for_extension(url)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
