from __future__ import annotations

import csv
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus
from road2ai_vifinqa.panel import FinancialPanel
from road2ai_vifinqa.template_solver import TemplateSolver, _AUDITED_OVERRIDES, _fold, _strip_metric_wrappers


EXTRACT = ROOT / "tmp" / "vn53_analysis_20260824"
records = {
    int(item["id"]): item
    for item in json.loads((EXTRACT / "submission.json").read_text(encoding="utf-8"))
}


def score(metric: str, label: str) -> float:
    left = _strip_metric_wrappers(metric)
    right = _strip_metric_wrappers(label)
    return SequenceMatcher(None, left, right).ratio()


output: list[dict[str, object]] = []
with Corpus() as corpus:
    solver = TemplateSolver(corpus, FinancialPanel())
    for qid in range(578, 1013):
        if qid in _AUDITED_OVERRIDES:
            continue
        record = records[qid]
        plan = solver.parse(str(record["question"]), question_id=qid)
        csv_path = EXTRACT / str(record["evidence"][0]["csv_path"])
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        labels = [str(row.get("label", "")) for row in rows]
        scores = [score(plan.metric, label) for label in labels]
        output.append(
            {
                "qid": qid,
                "question": record["question"],
                "answer": record["answer"],
                "metric": plan.metric,
                "operation": plan.operation,
                "labels": labels,
                "scores": scores,
                "min_score": min(scores, default=1.0),
                "mean_score": sum(scores) / max(len(scores), 1),
                "sources": [
                    {
                        key: row.get(key, "")
                        for key in ("ticker", "year", "doc_id", "table_id", "row_idx", "col_idx", "raw_value", "label")
                    }
                    for row in rows
                ],
            }
        )

output.sort(key=lambda item: (float(item["mean_score"]), float(item["min_score"])))
path = ROOT / "runs" / "live_search" / "template_metric_alignment_scan.json"
path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for item in output[:80]:
    print(
        f"Q{item['qid']} mean={item['mean_score']:.3f} min={item['min_score']:.3f} "
        f"op={item['operation']} metric={item['metric']!r} answer={item['answer']}"
    )
    print(f"  labels={item['labels']}")
    print(f"  {item['question']}")
