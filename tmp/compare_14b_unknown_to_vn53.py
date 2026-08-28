import json
import zipfile
from pathlib import Path


with zipfile.ZipFile("submission_vn53.zip") as archive:
    baseline = {
        int(row["id"]): row
        for row in json.loads(archive.read("submission.json").decode("utf-8"))
    }

files = [
    Path("runs/live_search/easy_14b_risk_results.json"),
    Path("runs/live_search/easy_14b_batch2_results.json"),
    Path("runs/live_search/easy_q4_risk20_results.json"),
    Path("runs/live_search/easy_q4_benchmark_results.json"),
]
seen = set()
for path in files:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", {})
    for key, result in rows.items():
        qid = int(key)
        if result.get("error") or "answer" not in result:
            continue
        old = float(baseline[qid]["answer"])
        new = float(result["answer"])
        if abs(old - new) <= 1e-10 * max(1.0, abs(old), abs(new)):
            continue
        signature = (qid, round(new, 12))
        if signature in seen:
            continue
        seen.add(signature)
        selected = (result.get("selected") or [{}])[0]
        print(
            f"{path.stem} Q{qid} old={old} new={new}\n"
            f"  {baseline[qid]['question']}\n"
            f"  ALT {selected.get('doc_id')}|{selected.get('table_id')} "
            f"r{selected.get('row_idx')}c{selected.get('col_idx')} "
            f"{selected.get('row_label')} raw={selected.get('raw_value')}"
        )
