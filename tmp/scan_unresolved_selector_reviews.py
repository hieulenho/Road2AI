import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QIDS = {16, 35, 82, 111, 120, 135, 166, 182, 194, 221, 411, 442, 473, 490, 568, 582, 611, 616, 635, 641, 676, 701, 923}

for path in sorted((ROOT / "runs" / "reasoning_selector").glob("*.json")):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    rows = payload.get("rows", {}) if isinstance(payload, dict) else {}
    if not isinstance(rows, dict):
        continue
    for key, row in rows.items():
        try:
            qid = int(row.get("id", key))
        except (TypeError, ValueError):
            continue
        if qid not in QIDS:
            continue
        selected = row.get("selected", {})
        selection = row.get("selection", {})
        review = row.get("review", {})
        print(
            json.dumps(
                {
                    "id": qid,
                    "file": path.name,
                    "baseline": row.get("baseline"),
                    "changed": row.get("changed"),
                    "selected_answer": selected.get("answer_value") if isinstance(selected, dict) else None,
                    "selected_raw": selected.get("raw_value") if isinstance(selected, dict) else None,
                    "confidence": selection.get("confidence") if isinstance(selection, dict) else None,
                    "approx": review.get("approximate_answer") if isinstance(review, dict) else None,
                },
                ensure_ascii=False,
            )
        )
