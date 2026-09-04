import json
import math
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
with zipfile.ZipFile(ROOT / "submission_vn70.zip") as archive:
    rows = json.loads(archive.read("submission.json"))
    baseline = {int(row["id"]): float(row["answer"]) for row in rows}


def normalize(question, value, unit):
    q = question.lower()
    u = str(unit or "").lower()
    raw_money = bool(re.search(r"\b(vnd|vnđ)\b", u)) and not any(
        marker in u for marker in ("triệu", "tỷ", "nghìn", "hundred", "billion", "million")
    )
    if raw_money:
        if "nghìn tỷ" in q:
            return value / 1e12
        if "trăm tỷ" in q:
            return value / 1e11
        if "tỷ đồng" in q:
            return value / 1e9
        if "triệu đồng" in q or "triệu vn" in q:
            return value / 1e6
        if "nghìn đồng" in q:
            return value / 1e3
    return value


seen = set()
items = []
for path in sorted((ROOT / "runs" / "reasoning_selector").glob("*.json")):
    if "_input" in path.name:
        continue
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    rows = payload.get("rows", {}) if isinstance(payload, dict) else {}
    if not isinstance(rows, dict):
        continue
    for key, row in rows.items():
        review = row.get("review") if isinstance(row, dict) else None
        if not isinstance(review, dict) or review.get("approximate_answer") is None:
            continue
        try:
            qid = int(row.get("id", key))
            approx = float(review["approximate_answer"])
            base = baseline[qid]
        except (TypeError, ValueError, KeyError):
            continue
        if not math.isfinite(approx):
            continue
        question = str(row.get("question", ""))
        unit = review.get("answer_unit")
        adjusted = normalize(question, approx, unit)
        rel = abs(adjusted - base) / max(1.0, abs(adjusted), abs(base))
        if rel < 1e-5:
            continue
        signature = (qid, round(adjusted, 8))
        if signature in seen:
            continue
        seen.add(signature)
        items.append(
            {
                "id": qid,
                "base": base,
                "approx": approx,
                "adjusted": adjusted,
                "relative_delta": rel,
                "unit": unit,
                "issues": len(review.get("issues", [])),
                "missing": review.get("missing_inputs", []),
                "calculation": review.get("calculation"),
                "question": question,
                "file": path.name,
            }
        )

for item in sorted(items, key=lambda item: (len(item["missing"]) > 0, item["issues"] > 0, -item["relative_delta"])):
    print(json.dumps(item, ensure_ascii=False))
