from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from road2ai_vifinqa.text import fold_text


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tmp" / "vn53_analysis_20260824"
RECORDS = json.loads((EXTRACT / "submission.json").read_text(encoding="utf-8"))

TOTAL_MARKERS = ("tong", "tong cong", "toan bo", "tat ca", "luy ke")
COUNT_MARKERS = (
    "co bao nhieu",
    "trong so",
    "so cong ty",
    "so nam",
    "so don vi",
    "dem so",
)
MEAN_MARKERS = ("trung binh", "binh quan")
QUESTION_AGG_MARKERS = TOTAL_MARKERS + COUNT_MARKERS + MEAN_MARKERS


def read_rows(record: dict[str, object]) -> list[dict[str, str]]:
    evidence = record.get("evidence") or []
    if not evidence:
        return []
    csv_path = EXTRACT / str(evidence[0]["csv_path"])
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def has_any(text: str, markers: tuple[str, ...]) -> bool:
    padded = f" {text} "
    return any(f" {marker} " in padded for marker in markers)


def row_summary(row: dict[str, str]) -> dict[str, object]:
    return {
        key: row.get(key, "")
        for key in (
            "ticker",
            "year",
            "doc_id",
            "table_id",
            "row_idx",
            "col_idx",
            "raw_value",
            "label",
        )
    }


findings: list[dict[str, object]] = []
for record in RECORDS:
    qid = int(record["id"])
    question = str(record["question"])
    folded_q = fold_text(question)
    if not has_any(folded_q, QUESTION_AGG_MARKERS):
        continue

    rows = read_rows(record)
    folded_labels = [fold_text(row.get("label", "")) for row in rows]
    tickers = [row.get("ticker", "") for row in rows if row.get("ticker", "")]
    ticker_counts = Counter(tickers)
    duplicate_tickers = {key: value for key, value in ticker_counts.items() if value > 1}
    blank_labels = sum(not label for label in folded_labels)
    label_has_total = [has_any(label, TOTAL_MARKERS) for label in folded_labels]
    question_has_total = has_any(folded_q, TOTAL_MARKERS)
    question_has_count = has_any(folded_q, COUNT_MARKERS)
    question_has_mean = has_any(folded_q, MEAN_MARKERS)

    reasons: list[str] = []
    risk = 0
    if question_has_total and rows and not any(label_has_total):
        reasons.append("total-question-without-total-labelled-source")
        risk += 4
    if question_has_total and len(rows) > 1 and not all(label_has_total):
        reasons.append("mixed-total-and-component-sources")
        risk += 2
    if blank_labels:
        reasons.append(f"blank-source-labels:{blank_labels}")
        risk += min(blank_labels, 3)
    if question_has_count and duplicate_tickers:
        reasons.append(f"duplicate-tickers-in-count:{duplicate_tickers}")
        risk += 4
    if question_has_mean and duplicate_tickers:
        reasons.append(f"duplicate-tickers-in-mean:{duplicate_tickers}")
        risk += 3
    if question_has_count and len(rows) == 1:
        reasons.append("count-answer-derived-from-single-evidence-row")
        risk += 1

    if risk:
        findings.append(
            {
                "qid": qid,
                "risk": risk,
                "reasons": reasons,
                "question": question,
                "answer": record["answer"],
                "row_count": len(rows),
                "sources": [row_summary(row) for row in rows],
            }
        )

findings.sort(key=lambda item: (-int(item["risk"]), int(item["qid"])))
output = ROOT / "runs" / "live_search" / "aggregate_source_risk_scan.json"
output.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for item in findings[:120]:
    print(f"Q{item['qid']} risk={item['risk']} answer={item['answer']} {', '.join(item['reasons'])}")
    print(f"  {item['question']}")
    for source in item["sources"][:15]:
        print(
            "  - "
            + " ".join(
                f"{key}={value}"
                for key, value in source.items()
                if value not in (None, "")
            )
        )
    if len(item["sources"]) > 15:
        print(f"  ... {len(item['sources']) - 15} more source rows")
