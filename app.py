

from flask import Flask, request, redirect, url_for, render_template_string
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from datetime import datetime, timezone
from uuid import uuid4

app = Flask(__name__)

AWS_REGION = "ap-south-1"
TABLE_NAME = "CloudOpsDeployments"

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEXUS | CloudOps Control Center</title>
<style>
* { box-sizing: border-box; }
:root {
  --bg: #070b14;
  --panel: #0d1524;
  --line: #23334a;
  --cyan: #48f0e0;
  --blue: #6c8cff;
  --text: #e9f3ff;
  --muted: #91a4bd;
}
body {
  margin: 0;
  background:
    radial-gradient(ellipse at 80% 0%, #12294a 0%, transparent 35%),
    var(--bg);
  color: var(--text);
  font-family: "Segoe UI", Arial, sans-serif;
}
nav {
  padding: 20px 6%;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #080e1beF;
}
.brand { font-size: 23px; font-weight: 900; letter-spacing: 3px; }
.brand span { color: var(--cyan); }
.nav-right { color: var(--muted); font-size: 12px; }
main { max-width: 1250px; margin: auto; padding: 45px 24px; }
.eyebrow { color: var(--cyan); font-size: 11px; letter-spacing: 3px; }
h1 { font-size: clamp(32px, 5vw, 54px); margin: 12px 0; letter-spacing: -1px; }
h1 span { color: var(--cyan); }
.subtitle { color: var(--muted); max-width: 680px; line-height: 1.8; }
.statusbar {
  display: flex; flex-wrap: wrap; gap: 12px;
  margin: 30px 0;
}
.pill {
  border: 1px solid var(--line); background: #0d1929;
  border-radius: 7px; padding: 10px 14px;
  font-size: 12px; color: #c6d7ec;
}
.dot { color: var(--cyan); margin-right: 8px; }
.layout {
  display: grid; grid-template-columns: 360px minmax(0, 1fr);
  gap: 22px; align-items: start;
}
.panel {
  background: linear-gradient(145deg, #101b2d, #0a111f);
  border: 1px solid var(--line);
  border-radius: 14px; padding: 23px;
  box-shadow: 0 12px 40px #00000024;
}
.panel h2 { font-size: 18px; margin: 0 0 6px; }
.description { color: var(--muted); font-size: 12px; margin-bottom: 22px; }
label {
  display: block; font-size: 12px; color: #b9cbe0;
  margin: 17px 0 8px;
}
input, select {
  width: 100%; padding: 12px; border-radius: 7px;
  border: 1px solid #30415a; background: #080f1c;
  color: white; outline: none; font: inherit;
}
input:focus, select:focus { border-color: var(--cyan); }
button, .button {
  cursor: pointer; border: 0; border-radius: 7px;
  background: linear-gradient(100deg, #17bdb8, #538bff);
  color: #06101b; padding: 12px 17px;
  font-weight: 800; font-size: 12px; text-decoration: none;
}
button:hover, .button:hover { filter: brightness(1.15); }
.submit { width: 100%; margin-top: 23px; }
.message {
  border: 1px solid #26695f; background: #102a2a;
  color: #8cf7dc; border-radius: 8px; padding: 12px;
  font-size: 13px; margin-bottom: 20px;
  overflow-wrap: anywhere;
}
.error { border-color: #85434b; background: #301923; color: #ffb6bd; }
.records-head {
  display: flex; flex-wrap: wrap; justify-content: space-between;
  align-items: center; gap: 12px; margin-bottom: 20px;
}
.records-head h2 { margin: 0; }
.count { color: var(--cyan); font-size: 12px; }
.record {
  border: 1px solid var(--line); background: #0b1423;
  border-radius: 9px; padding: 17px; margin-top: 12px;
}
.record-top {
  display: flex; justify-content: space-between;
  align-items: start; gap: 10px;
}
.record h3 { margin: 0 0 7px; font-size: 15px; overflow-wrap: anywhere; }
.record-id { color: #7890ad; font-size: 10px; overflow-wrap: anywhere; }
.badge {
  border: 1px solid #245b53; background: #102c29;
  color: #7cf4d7; border-radius: 20px;
  padding: 5px 9px; font-size: 10px; white-space: nowrap;
}
.badge.failed { color: #ffb2bb; border-color: #773b48; background: #301a23; }
.badge.pending { color: #ffdb91; border-color: #705c32; background: #2b2518; }
.meta {
  display: flex; flex-wrap: wrap; gap: 9px 20px;
  margin-top: 16px; color: var(--muted); font-size: 11px;
}
.empty {
  text-align: center; padding: 40px 15px;
  color: var(--muted); border: 1px dashed #30415a; border-radius: 10px;
}
.empty strong { display: block; color: #c6d7ec; margin-bottom: 8px; }
footer {
  border-top: 1px solid var(--line); color: #71849d;
  text-align: center; padding: 24px; font-size: 11px; margin-top: 35px;
}
@media (max-width: 850px) {
  .layout { grid-template-columns: 1fr; }
}
@media (max-width: 500px) {
  main { padding: 30px 14px; }
  nav { padding: 17px 14px; }
  .brand { font-size: 18px; }
  .nav-right { font-size: 10px; }
  .panel { padding: 17px; }
}
</style>
</head>
<body>
<nav>
  <div class="brand">NEXUS<span>_</span>OPS</div>
  <div class="nav-right">CLOUD CONTROL CENTER / v1.0</div>
</nav>

<main>
  <div class="eyebrow">SYSTEM / DEPLOYMENT MANAGEMENT</div>
  <h1>Command your <span>cloud.</span></h1>
  <p class="subtitle">
    A Python-powered deployment manager connected to Amazon DynamoDB.
    Create deployment records, persist them in AWS, and inspect your
    project's activity from one futuristic control panel.
  </p>

  <div class="statusbar">
    <div class="pill"><span class="dot">●</span>FLASK APPLICATION</div>
    <div class="pill"><span class="dot">●</span>AMAZON DYNAMODB</div>
    <div class="pill">REGION / {{ region }}</div>
  </div>

  {% if message %}
    <div class="message {{ 'error' if is_error else '' }}">{{ message }}</div>
  {% endif %}

  <div class="layout">
    <section class="panel">
      <h2>New deployment</h2>
      <div class="description">Create a record in your AWS database.</div>

      <form method="POST" action="{{ url_for('create_deployment') }}">
        <label for="project_name">PROJECT NAME</label>
        <input id="project_name" name="project_name"
               maxlength="80" required
               placeholder="e.g. ecommerce-api">

        <label for="environment">TARGET ENVIRONMENT</label>
        <select id="environment" name="environment" required>
          <option value="Development">Development</option>
          <option value="Testing">Testing</option>
          <option value="Staging">Staging</option>
          <option value="Production">Production</option>
        </select>

        <label for="status">DEPLOYMENT STATUS</label>
        <select id="status" name="status" required>
          <option value="Pending">Pending</option>
          <option value="In Progress">In Progress</option>
          <option value="Successful">Successful</option>
          <option value="Failed">Failed</option>
        </select>

        <button class="submit" type="submit">＋ SAVE DEPLOYMENT RECORD</button>
      </form>
    </section>

    <section class="panel">
      <div class="records-head">
        <div>
          <h2>Deployment registry</h2>
          <div class="description" style="margin:7px 0 0">
            Records retrieved from DynamoDB
          </div>
        </div>
        <div class="count">{{ records|length }} RECORD(S)</div>
      </div>

      {% if records %}
        {% for item in records %}
          <article class="record">
            <div class="record-top">
              <div>
                <h3>{{ item.get('project_name', 'Unnamed project') }}</h3>
                <div class="record-id">ID / {{ item.get('deployment_id', '') }}</div>
              </div>
              {% set s = item.get('status', 'Pending') %}
              <span class="badge {{ 'failed' if s == 'Failed' else 'pending' if s in ['Pending', 'In Progress'] else '' }}">
                {{ s }}
              </span>
            </div>
            <div class="meta">
              <span>ENV / {{ item.get('environment', 'N/A') }}</span>
              <span>CREATED / {{ item.get('created_at', 'N/A') }}</span>
            </div>
          </article>
        {% endfor %}
      {% else %}
        <div class="empty">
          <strong>NO DEPLOYMENT RECORDS FOUND</strong>
          Submit your first record using the form. It will be saved
          to the CloudOpsDeployments DynamoDB table.
        </div>
      {% endif %}
    </section>
  </div>
</main>

<footer>
  NEXUS OPS · BUILT WITH PYTHON, FLASK & AMAZON DYNAMODB
  <br><br>
  Learning project · Deployment statuses are user-entered records,
  not live AWS deployment telemetry.
</footer>
</body>
</html>
"""


def get_records():
    response = table.scan()
    records = response.get("Items", [])

    # Continue reading if DynamoDB returns paginated results.
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        records.extend(response.get("Items", []))

    records.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )
    return records


@app.route("/")
def home():
    message = request.args.get("message", "")
    is_error = request.args.get("error") == "1"

    try:
        records = get_records()
    except (ClientError, BotoCoreError) as exc:
        app.logger.exception("Unable to read DynamoDB records")
        records = []
        message = (
            "Could not read DynamoDB. Check your AWS region, "
            "credentials, table name, and IAM permissions."
        )
        is_error = True

    return render_template_string(
        PAGE,
        records=records,
        message=message,
        is_error=is_error,
        region=AWS_REGION
    )


@app.route("/deployments", methods=["POST"])
def create_deployment():
    project_name = request.form.get("project_name", "").strip()
    environment = request.form.get("environment", "")
    status = request.form.get("status", "")

    allowed_environments = {
        "Development", "Testing", "Staging", "Production"
    }
    allowed_statuses = {
        "Pending", "In Progress", "Successful", "Failed"
    }

    if (
        not project_name
        or environment not in allowed_environments
        or status not in allowed_statuses
    ):
        return redirect(url_for(
            "home",
            message="Please provide valid deployment details.",
            error="1"
        ))

    now = datetime.now(timezone.utc).isoformat()

    item = {
        "deployment_id": str(uuid4()),
        "project_name": project_name,
        "environment": environment,
        "status": status,
        "created_at": now
    }

    try:
        table.put_item(Item=item)
    except (ClientError, BotoCoreError):
        app.logger.exception("Unable to save deployment")
        return redirect(url_for(
            "home",
            message=(
                "Could not save the record. Check AWS credentials, "
                "region, table name, and PutItem permissions."
            ),
            error="1"
        ))

    return redirect(url_for(
        "home",
        message="Deployment record saved successfully to DynamoDB."
    ))


if __name__ == "__main__":
    app.run(debug=True)
