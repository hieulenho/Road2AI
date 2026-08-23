from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path


ZIP_PATH = Path("submission_vn53.zip")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def years(text: str) -> set[int]:
    return {int(x) for x in re.findall(r"\b20(?:1[5-9]|2[0-5])\b", text)}


with zipfile.ZipFile(ZIP_PATH) as zf:
    rows = json.loads(zf.read("submission.json"))
    findings: list[dict[str, object]] = []
    for item in rows:
        qid = int(item["id"])
        if qid % 2 == 0:
            continue
        q = str(item["question"])
        qn = norm(q)
        q_years = years(q)
        evidence_rows: list[dict[str, str]] = []
        for ev in item.get("evidence", []):
            name = str(ev["csv_path"])
            evidence_rows.extend(csv.DictReader(io.StringIO(zf.read(name).decode("utf-8-sig"))))
        labels = [str(row.get("label", "")) for row in evidence_rows]
        docs = [str(row.get("doc_id", "")) for row in evidence_rows]
        ev_years = {int(row["year"]) for row in evidence_rows if str(row.get("year", "")).isdigit()}
        flags: list[str] = []
        if q_years and not ev_years.issubset(q_years):
            flags.append(f"year:{sorted(q_years)}!={sorted(ev_years)}")
        asks_parent = any(tok in qn for tok in ("cong ty me", "bao cao rieng", "bctc rieng"))
        asks_consolidated = any(tok in qn for tok in ("hop nhat", "toan tap doan"))
        if asks_parent and any("consolidated" in doc for doc in docs):
            flags.append("parent_uses_consolidated")
        if asks_consolidated and any("separate" in doc for doc in docs):
            flags.append("consolidated_uses_separate")
        asks_total = bool(re.search(r"\b(tong|tong cong|toan bo)\b", qn))
        label_norm = " | ".join(norm(x) for x in labels)
        if asks_total and not re.search(r"\b(tong|tong cong|cong)\b", label_norm):
            flags.append("asks_total_no_total_label")
        if flags:
            findings.append(
                {
                    "qid": qid,
                    "question": q,
                    "answer": item["answer"],
                    "flags": flags,
                    "labels": labels,
                    "docs": docs,
                }
            )

for finding in findings:
    print(json.dumps(finding, ensure_ascii=False))
print(f"COUNT={len(findings)}")
