from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus  # noqa: E402
from road2ai_vifinqa.template_solver import _fold  # noqa: E402


EXTRACT = ROOT / "tmp" / "vn53_analysis_20260824"
records = {
    int(item["id"]): item
    for item in json.loads((EXTRACT / "submission.json").read_text(encoding="utf-8"))
}
flags: list[dict[str, object]] = []


def last_section(rows: tuple[tuple[str, ...], ...], row_idx: int) -> str:
    result = ""
    for cells in rows[:row_idx]:
        text = " ".join(cell for cell in cells if cell).strip()
        folded = _fold(text)
        if (
            "nam truoc" in folded
            or "nam nay" in folded
            or "ky truoc" in folded
            or "ky nay" in folded
            or re.fullmatch(r"(nam )?(20\d{2})", folded)
        ):
            result = text
    return result


with Corpus() as corpus:
    for qid in range(578, 1013):
        record = records[qid]
        csv_path = EXTRACT / str(record["evidence"][0]["csv_path"])
        with csv_path.open(encoding="utf-8-sig", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        for source in source_rows:
            if (
                not source.get("doc_id")
                or not source.get("table_id")
                or not source.get("row_idx")
                or source.get("col_idx") in (None, "")
            ):
                continue
            doc_id = str(source["doc_id"])
            table_id = int(source["table_id"])
            row_idx = int(source["row_idx"])
            col_idx = int(source["col_idx"])
            year = int(float(source["year"]))
            table = corpus.table(doc_id, table_id)
            section = last_section(table.rows, row_idx)
            folded = _fold(section)
            prior = "nam truoc" in folded or "ky truoc" in folded
            explicit_years = [int(value) for value in re.findall(r"20\d{2}", section)]
            wrong_year = bool(explicit_years and year not in explicit_years)
            header = " | ".join(
                str(row[col_idx])
                for row in table.rows[:row_idx]
                if col_idx < len(row) and row[col_idx]
            )
            header_folded = _fold(header)
            prior_header = "nam truoc" in header_folded or "ky truoc" in header_folded
            header_years = [int(value) for value in re.findall(r"20\d{2}", header)]
            wrong_header_year = bool(header_years and year not in header_years)
            if prior or wrong_year or prior_header or wrong_header_year:
                flags.append(
                    {
                        "qid": qid,
                        "question": record["question"],
                        "answer": record["answer"],
                        "source_id": source.get("source_id"),
                        "year": year,
                        "doc_id": doc_id,
                        "table_id": table_id,
                        "row_idx": row_idx,
                        "col_idx": col_idx,
                        "label": source.get("label"),
                        "raw_value": source.get("raw_value"),
                        "section": section,
                        "header": header,
                        "prior_section": prior,
                        "wrong_section_year": wrong_year,
                        "prior_header": prior_header,
                        "wrong_header_year": wrong_header_year,
                    }
                )

path = ROOT / "runs" / "live_search" / "template_period_section_scan.json"
path.write_text(json.dumps(flags, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for item in flags:
    print(
        f"Q{item['qid']} {item['doc_id']} T{item['table_id']} R{item['row_idx']}C{item['col_idx']} "
        f"year={item['year']} label={item['label']!r} raw={item['raw_value']}"
    )
    print(f"  section={item['section']!r}")
    print(f"  header={item['header']!r}")
    print(f"  {item['question']}")
