"""Read-only compact summary of prior source-only reviews."""

from __future__ import annotations

import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for name in glob.glob(str(ROOT / "runs" / "reasoning_selector" / "qwen35_easy*2026083*.json")):
    path = Path(name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(f"FILE {path.name}; rows={len(payload.get('rows', {}))}")
    for key, row in payload.get("rows", {}).items():
        if row.get("changed"):
            selected = row.get("selected", {})
            print(
                f"CHANGE Q{int(key):04d} old={row.get('baseline')!r} "
                f"new={selected.get('answer_value')!r} coordinate="
                f"{selected.get('doc_id')}|{selected.get('table_id')}|"
                f"{selected.get('row_idx')}|{selected.get('col_idx')}"
            )
        review = row.get("review", {})
        issues = review.get("issues", [])
        missing = review.get("missing_inputs", [])
        approximate = review.get("approximate_answer")
        if issues or missing or approximate is not None:
            print(
                f"Q{int(key):04d} issues={len(issues)} missing={len(missing)} "
                f"answer={approximate!r} calculation={str(review.get('calculation', ''))[:260]!r}"
            )
