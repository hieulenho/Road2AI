import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for path in sorted((ROOT / "runs" / "reasoning_selector").glob("*.json")):
    if "_input" in path.name or "manifest" in path.name or "plan" in path.name:
        continue
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    rows = payload.get("rows", {}) if isinstance(payload, dict) else {}
    if not isinstance(rows, dict):
        continue
    for key, row in rows.items():
        if not isinstance(row, dict) or not row.get("changed"):
            continue
        print(
            json.dumps(
                {
                    "id": int(row.get("id", key)),
                    "baseline": row.get("baseline"),
                    "answer": row.get("answer"),
                    "selected_answer": (row.get("selected") or {}).get("answer_value"),
                    "confidence": (row.get("selection") or {}).get("confidence"),
                    "error": row.get("error"),
                    "question": row.get("question"),
                    "file": path.name,
                },
                ensure_ascii=False,
            )
        )
