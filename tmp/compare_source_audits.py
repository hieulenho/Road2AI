import json
import math
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
with zipfile.ZipFile(ROOT / "submission_vn70.zip") as archive:
    member = next(name for name in archive.namelist() if name.endswith(".json"))
    current = {int(row["id"]): row for row in json.loads(archive.read(member))}


def rows_from(payload):
    rows = payload.get("rows", payload) if isinstance(payload, dict) else payload
    if isinstance(rows, dict):
        return rows.items()
    if isinstance(rows, list):
        return ((str(row.get("id", "")), row) for row in rows if isinstance(row, dict))
    return ()


seen = set()
candidates = []
for path in (ROOT / "runs" / "reasoning_selector").glob("*.json"):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    for key, row in rows_from(payload):
        if not isinstance(row, dict):
            continue
        review = row.get("review", row)
        if not isinstance(review, dict) or "approximate_answer" not in review:
            continue
        try:
            qid = int(row.get("id", key))
            approx = float(review["approximate_answer"])
            base = float(current[qid]["answer"])
        except (TypeError, ValueError, KeyError):
            continue
        if not (math.isfinite(approx) and math.isfinite(base)):
            continue
        rel = abs(approx - base) / max(1.0, abs(base), abs(approx))
        if rel < 1e-8:
            continue
        signature = (qid, round(approx, 9))
        if signature in seen:
            continue
        seen.add(signature)
        candidates.append(
            {
                "id": qid,
                "base": base,
                "approx": approx,
                "relative_delta": rel,
                "file": path.name,
                "question": current[qid].get("question", ""),
                "calculation": review.get("calculation"),
                "unit": review.get("answer_unit"),
                "missing": review.get("missing_inputs", []),
            }
        )

for item in sorted(candidates, key=lambda x: (-x["relative_delta"], x["id"])):
    print(json.dumps(item, ensure_ascii=False))
