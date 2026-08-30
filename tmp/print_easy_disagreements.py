import json
import glob


seen = set()
for path in glob.glob("runs/reasoning_selector/*qwen35*.json"):
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        continue
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), dict):
        continue
    seen.update(int(key) for key in payload["rows"])

with open(
    "runs/agent_generator_reverse_map/unoverridden_generator_queue.json",
    encoding="utf-8",
) as handle:
    rows = json.load(handle)

rows = [
    row for row in rows
    if row.get("top_differs_current") and row["id"] not in seen
]
rows.sort(key=lambda row: (-row["top_table_margin"], -row["margin_over_current"]))

shown = 0
for row in rows:
    current = row.get("current") or {}
    top = row.get("top") or {}
    if not row.get("top_differs_current"):
        continue
    shown += 1
    print(
        f"Q{row['id']} margin={row['margin_over_current']:.2f} "
        f"table_margin={row['top_table_margin']:.2f}"
    )
    print(" ", row["question"])
    print(
        " CUR",
        row["current_answer"],
        current.get("row_label"),
        "|",
        current.get("column_header"),
        "T",
        current.get("table_id"),
    )
    print(
        " TOP",
        top.get("answer_value"),
        top.get("row_label"),
        "|",
        top.get("column_header"),
        "T",
        top.get("table_id"),
    )
    if shown >= 80:
        break

print(f"seen={len(seen)} remaining_differing={len(rows)}")
