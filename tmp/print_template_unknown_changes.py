import json
from pathlib import Path


d = json.loads(
    Path("runs/live_search/template_on_unknown_easy.json").read_text(encoding="utf-8")
)
rows = [row for row in d["rows"] if not row["same_answer"]]
rows.sort(key=lambda row: -float(row["confidence"]))
for row in rows:
    source = row["sources"][0] if row["sources"] else {}
    print(
        f"Q{row['id']} conf={row['confidence']:.3f} "
        f"current={row['current_answer']} alt={row['template_answer']}\n"
        f"  {row['question']}\n"
        f"  ALT {source.get('doc_id')}|{source.get('table_id')} "
        f"r{source.get('row_idx')}c{source.get('col_idx')} "
        f"{source.get('label')} raw={source.get('raw_value')}"
    )
