import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
with zipfile.ZipFile(ROOT / "submission_vn70.zip") as archive:
    member = next(name for name in archive.namelist() if name.endswith(".json"))
    current = {int(row["id"]): row for row in json.loads(archive.read(member))}

for path in sorted((ROOT / "runs" / "live_search").glob("qwen14_exact_easy_unknown_*.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload.get("rows", {}).values():
        if not row.get("changed") or not row.get("selected"):
            continue
        qid = int(row["id"])
        selected = row["selected"]
        print(
            json.dumps(
                {
                    "id": qid,
                    "risk": row.get("risk"),
                    "current": current[qid]["answer"],
                    "candidate": selected.get("answer_value"),
                    "doc": selected.get("doc_id"),
                    "table": selected.get("table_id"),
                    "row": selected.get("row_idx"),
                    "col": selected.get("col_idx"),
                    "label": selected.get("row_label"),
                    "header": selected.get("column_header"),
                    "question": row.get("question"),
                    "file": path.name,
                },
                ensure_ascii=False,
            )
        )
