import json
import sys

from road2ai_vifinqa.retrieval import STOPWORDS, metric_phrase
from road2ai_vifinqa.text import fold_text


queue = json.load(open("runs/agent_easy_resolver_cv/unoverridden_review_queue.json", encoding="utf-8"))
rows = []
for item in queue:
    current = (item.get("current") or [{}])[0]
    metric = [token for token in metric_phrase(item["question"]).split() if token not in STOPWORDS]
    evidence = fold_text(
        " ".join(
            str(current.get(key, ""))
            for key in ("row_label", "section", "column_header", "table_context")
        )
    )
    matched = [token for token in metric if token in evidence]
    coverage = len(matched) / max(1, len(metric))
    rows.append((coverage, int(item["id"]), metric, matched, item, current))

rows.sort(key=lambda value: (value[0], value[1]))
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 80
for coverage, qid, metric, matched, item, current in rows[:limit]:
    print(f"Q{qid} coverage={coverage:.3f} status={item['audit_status']} conf={item['confidence']:.3f}")
    print(f"  {item['question']}")
    print(f"  metric={metric} matched={matched}")
    print(
        f"  CUR {item['current_answer']} | {current.get('row_label')} | "
        f"{current.get('column_header')} | t{current.get('table_id')} "
        f"r{current.get('row_idx')}c{current.get('col_idx')}"
    )
    print(f"  context={str(current.get('table_context', ''))[:220]}")
