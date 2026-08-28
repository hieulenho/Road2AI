import json
import sys


payload = json.load(open("runs/agent_easy_resolver_cv/unoverridden_review_queue.json", encoding="utf-8"))
limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(payload)
risky_only = "--risky" in sys.argv
for item in payload[:limit]:
    if risky_only and item.get("audit_status") not in {"changed", "disagreed_kept", "audit_failed"}:
        continue
    current = (item.get("current") or [{}])[0]
    top = item.get("top") or {}
    if abs(float(item.get("current_answer", 0)) - float(top.get("answer_value", 0))) < 1e-12:
        continue
    print(f"Q{item['id']} status={item['audit_status']} conf={item['confidence']} rank={item['current_rank']} margin={item['score_margin_over_current']:.3f}")
    print(f"  {item['question']}")
    print(f"  CUR {item['current_answer']} | {current.get('row_label')} | {current.get('column_header')} | t{current.get('table_id')} r{current.get('row_idx')}c{current.get('col_idx')}")
    print(f"  ALT {top.get('answer_value')} | {top.get('row_label')} | {top.get('column_header')} | t{top.get('table_id')} r{top.get('row_idx')}c{top.get('col_idx')}")
