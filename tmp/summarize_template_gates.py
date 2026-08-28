import glob
import json
import os


for path in glob.glob("runs/live_search/qwen14_template_unknown*_gate.json"):
    payload = json.load(open(path, encoding="utf-8"))
    rows = payload.get("rows", {})
    accepted = [key for key, row in rows.items() if row.get("accepted_change")]
    print(os.path.basename(path), "tasks", len(rows), "accepted_changes", accepted)
