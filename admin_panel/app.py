import os
import base64
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_OWNER = os.environ["REPO_OWNER"]
REPO_NAME = os.environ["REPO_NAME"]
BRANCH = os.environ.get("BRANCH", "main")
WORKFLOW_FILE = os.environ.get("WORKFLOW_FILE", "build.yml")

API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def upload_zip_to_repo(file_bytes, path="source/source.zip"):
    """Commit the uploaded zip into the repo via the Contents API."""
    get_url = f"{API_BASE}/contents/{path}"
    r = requests.get(get_url, headers=HEADERS, params={"ref": BRANCH})
    sha = r.json().get("sha") if r.status_code == 200 else None

    content_b64 = base64.b64encode(file_bytes).decode("utf-8")
    payload = {
        "message": f"Upload source for build ({time.strftime('%Y-%m-%d %H:%M:%S')})",
        "content": content_b64,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put = requests.put(get_url, headers=HEADERS, json=payload)
    put.raise_for_status()
    return put.json()


def trigger_workflow(app_name, entry_file="main.py"):
    url = f"{API_BASE}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    payload = {
        "ref": BRANCH,
        "inputs": {"app_name": app_name, "entry_file": entry_file},
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()


def get_latest_run():
    url = f"{API_BASE}/actions/runs"
    r = requests.get(url, headers=HEADERS, params={"per_page": 1})
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])
    return runs[0] if runs else None


def get_latest_release_assets():
    url = f"{API_BASE}/releases"
    r = requests.get(url, headers=HEADERS, params={"per_page": 1})
    r.raise_for_status()
    releases = r.json()
    if not releases:
        return []
    return releases[0].get("assets", [])


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("source_zip")
    app_name = request.form.get("app_name", "MyApp").strip() or "MyApp"
    entry_file = request.form.get("entry_file", "main.py").strip() or "main.py"

    if not file or not file.filename.endswith(".zip"):
        flash("Please upload a valid .zip file.")
        return redirect(url_for("index"))

    file_bytes = file.read()
    upload_zip_to_repo(file_bytes)
    trigger_workflow(app_name, entry_file)

    flash("Uploaded and build triggered. Track progress on the status page.")
    return redirect(url_for("status"))


@app.route("/status", methods=["GET"])
def status():
    run = get_latest_run()
    assets = []
    if run and run.get("status") == "completed" and run.get("conclusion") == "success":
        assets = get_latest_release_assets()
    return render_template("status.html", run=run, assets=assets)


@app.route("/save/<asset_id>/<filename>", methods=["GET"])
def save_to_output(asset_id, filename):
    url = f"{API_BASE}/releases/assets/{asset_id}"
    headers = dict(HEADERS)
    headers["Accept"] = "application/octet-stream"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(r.content)
    return send_file(out_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
