import os
import requests
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from requests.auth import HTTPBasicAuth
from pprint import pprint
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
socketio = SocketIO(app, cors_allowed_origins="*")

# ─── Configuration ─────────────────────────────────────────────────────────────

API_TOKEN = "9106c1c8ffb9ca0ca3c5ee102791df0d"
USERNAME = "Yro"
SERVER = "http://localhost:8080"

# Store for tracking pipeline state changes
last_pipeline_state = None
current_run_id = None
update_interval = 5  # seconds

# ─── Helpers ───────────────────────────────────────────────────────────────────


def clean_steps(raw_steps: list) -> list:
    """
    Build a fresh dict for each step (no reuse!),
    pulling only the fields your template needs.
    """
    cleaned = []
    for s in raw_steps or []:
        cleaned.append(
            {
                "name": s.get("displayName") or s.get("name"),
                "status": s.get("result") or s.get("state"),
                "parameterDescription": s.get("displayDescription"),
            }
        )
    return cleaned


# ─── Pipeline Fetch ────────────────────────────────────────────────────────────
def hit_link(link: str, log_message: str, should_log: bool):
    link = SERVER + link.replace("/jenkins", "")

    if should_log:
        print(log_message)
        print(link)
    response = requests.get(link, auth=HTTPBasicAuth(USERNAME, API_TOKEN))

    if response.ok:
        data = response.json()
        # pprint(data)
    else:
        print(f"Error: {response.status_code}")
        return {}

    return data


def get_all_runs(limit=5):
    """Get multiple recent runs for comparison"""
    PIPELINE = "CC3"
    BRANCH = "master"
    url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs"

    try:
        resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        resp.raise_for_status()
        runs = resp.json() or []

        # Return basic info about recent runs
        return [
            {
                "id": run.get("id"),
                "name": run.get("name"),
                "status": run.get("status"),
                "startTimeMillis": run.get("startTimeMillis"),
                "durationMillis": run.get("durationMillis"),
                "queueDurationMillis": run.get("queueDurationMillis"),
            }
            for run in runs[:limit]
        ]
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return []


def get_pipeline(run_id=None) -> dict:
    """
    Gets pipeline data from Blue Ocean API for CC3
    """
    PIPELINE = "CC3"
    BRANCH = "master"

    try:
        if run_id:
            # Fetch specific run nodes
            url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs/{run_id}/nodes/"
        else:
            # Get latest run first
            runs_url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs?limit=1"
            resp = requests.get(runs_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
            resp.raise_for_status()
            runs = resp.json() or []
            
            if not runs:
                return {"stages": [], "runInfo": {}}
            
            run_id = runs[0].get("id")
            url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs/{run_id}/nodes/"
        
        # Get nodes/stages for the run
        resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        resp.raise_for_status()
        nodes = resp.json() or []

        # Get run info from runs list since direct endpoint might be empty
        run_info_url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs/?limit=10"
        run_resp = requests.get(run_info_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        run_resp.raise_for_status()
        runs_data = run_resp.json() or []
        
        # Find the specific run
        run_data = None
        for run in runs_data:
            if str(run.get("id")) == str(run_id):
                run_data = run
                break
        
        if not run_data:
            # Fallback to first run if not found
            run_data = runs_data[0] if runs_data else {}
        
        stages = []
        for node in nodes:
            # Get steps for each stage
            steps_url = f"{SERVER}/blue/rest/organizations/jenkins/pipelines/{PIPELINE}/branches/{BRANCH}/runs/{run_id}/nodes/{node['id']}/steps/"
            steps_resp = requests.get(steps_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
            steps_resp.raise_for_status()
            steps = steps_resp.json() or []
            
            stages.append(
                {
                    "name": node.get("displayName"),
                    "status": node.get("result") or node.get("state"),
                    "startTimeMillis": node.get("startTime"),
                    "durationMillis": node.get("durationInMillis"),
                    "stageFlowNodes": clean_steps(steps),
                }
            )

        # Include run information
        run_info = {
            "id": run_data.get("id"),
            "name": run_data.get("id"),  # Blue Ocean uses ID as name
            "status": run_data.get("result") or run_data.get("state"),
            "startTimeMillis": run_data.get("startTime"),
            "durationMillis": run_data.get("durationInMillis"),
            "queueDurationMillis": run_data.get("queueDurationMillis", 0),
            "causesString": "Manual run",  # You can extract this from causes if needed
        }

        return {"stages": stages, "runInfo": run_info}
    except Exception as e:
        print(f"Error fetching pipeline: {e}")
        return {"stages": [], "runInfo": {}}


def pipeline_has_changed(new_pipeline):
    """Check if the pipeline state has changed"""
    global last_pipeline_state, current_run_id

    new_run_id = new_pipeline.get("runInfo", {}).get("id")

    # Check if this is a new build
    is_new_build = False
    if current_run_id and new_run_id and current_run_id != new_run_id:
        is_new_build = True
        print(f"New build detected! Old: {current_run_id}, New: {new_run_id}")

    current_run_id = new_run_id

    # Convert to JSON string for comparison
    new_state = json.dumps(new_pipeline, sort_keys=True)

    if last_pipeline_state is None:
        last_pipeline_state = new_state
        return True, is_new_build

    if new_state != last_pipeline_state:
        last_pipeline_state = new_state
        return True, is_new_build

    return False, False


def background_pipeline_monitor():
    """Background thread that monitors Jenkins for changes"""
    while True:
        try:
            pipeline = get_pipeline()
            has_changed, is_new_build = pipeline_has_changed(pipeline)

            if has_changed:
                # Get recent runs for the run selector
                recent_runs = get_all_runs()

                # Emit update to all connected clients
                socketio.emit(
                    "pipeline_update",
                    {**pipeline, "isNewBuild": is_new_build, "recentRuns": recent_runs},
                    namespace="/",
                )

                if is_new_build:
                    print(
                        f"New build started - Run ID: {pipeline.get('runInfo', {}).get('id', 'unknown')}"
                    )
                else:
                    print(
                        f"Pipeline update sent - Run ID: {pipeline.get('runInfo', {}).get('id', 'unknown')}"
                    )
        except Exception as e:
            print(f"Error in background monitor: {e}")

        time.sleep(update_interval)


# ─── Socket Events ─────────────────────────────────────────────────────────────


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    # Send initial pipeline state with recent runs
    pipeline = get_pipeline()
    recent_runs = get_all_runs()
    emit("pipeline_update", {**pipeline, "recentRuns": recent_runs})


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("request_update")
def handle_update_request():
    """Handle manual update requests from client"""
    pipeline = get_pipeline()
    recent_runs = get_all_runs()
    emit("pipeline_update", {**pipeline, "recentRuns": recent_runs})


@socketio.on("switch_build")
def handle_switch_build(data):
    """Handle request to switch to a different build"""
    run_id = data.get("runId")
    print(f"Switching to build: {run_id}")
    pipeline = get_pipeline(run_id)
    recent_runs = get_all_runs()
    emit(
        "pipeline_update",
        {**pipeline, "recentRuns": recent_runs, "switchedBuild": True},
    )


# ─── Flask Routes ──────────────────────────────────────────────────────────────


@app.route("/")
def index():
    pipeline = get_pipeline()
    recent_runs = get_all_runs()
    return render_template(
        "index_websocket.html",
        stages=pipeline["stages"],
        runInfo=pipeline.get("runInfo", {}),
        recentRuns=recent_runs,
    )


@app.route("/api/pipeline")
def api_pipeline():
    """API endpoint for testing"""
    pipeline = get_pipeline()
    recent_runs = get_all_runs()
    return {**pipeline, "recentRuns": recent_runs}


# ─── Launcher ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=background_pipeline_monitor, daemon=True)
    monitor_thread.start()

    # Run the Socket.IO server
    socketio.run(app, debug=True, port=5001)
