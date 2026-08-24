from __future__ import annotations

import csv
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tmp" / "vn53_analysis_20260824"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = re.sub(r"\b(nam|so|tong|cong|trong|ky|cuoi|dau)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def similarity(values: list[str]) -> float:
    values = [norm(value) for value in values if norm(value)]
    if len(values) < 2:
        return 1.0
    scores = [
        SequenceMatcher(None, values[left], values[right]).ratio()
        for left in range(len(values))
        for right in range(left + 1, len(values))
    ]
    return sum(scores) / len(scores)


records = {
    int(item["id"]): item
    for item in json.loads((EXTRACT / "submission.json").read_text(encoding="utf-8"))
}

rows_out: list[dict[str, object]] = []
for qid in range(656, 1013):
    record = records[qid]
    question = str(record["question"])
    if not any(token in question.lower() for token in ("tỷ lệ", "tỉ lệ", "%", "biên lợi nhuận", "roe", "roa")):
        continue
    evidence = record["evidence"]
    if len(evidence) != 1:
        continue
    csv_path = EXTRACT / str(evidence[0]["csv_path"])
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) < 4 or len(rows) % 2:
        continue
    labels = [str(row.get("label", "")) for row in rows]
    numerator_labels = labels[0::2]
    denominator_labels = labels[1::2]
    rows_out.append(
        {
            "qid": qid,
            "answer": record["answer"],
            "question": question,
            "rows": len(rows),
            "numerator_similarity": similarity(numerator_labels),
            "denominator_similarity": similarity(denominator_labels),
            "numerator_labels": numerator_labels,
            "denominator_labels": denominator_labels,
            "sources": [
                {
                    key: row.get(key, "")
                    for key in ("ticker", "year", "doc_id", "table_id", "row_idx", "col_idx", "raw_value")
                }
                for row in rows
            ],
        }
    )

rows_out.sort(key=lambda item: min(float(item["numerator_similarity"]), float(item["denominator_similarity"])))
output = ROOT / "runs" / "live_search" / "template_ratio_homology_scan.json"
output.write_text(json.dumps(rows_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for item in rows_out[:40]:
    print(
        f"Q{item['qid']} n={item['numerator_similarity']:.3f} "
        f"d={item['denominator_similarity']:.3f} rows={item['rows']} "
        f"answer={item['answer']}"
    )
    print(f"  N: {item['numerator_labels']}")
    print(f"  D: {item['denominator_labels']}")
    print(f"  {item['question']}")
