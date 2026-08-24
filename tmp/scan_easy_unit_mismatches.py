from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tmp/vn53_analysis_20260824"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    submission = json.loads((BUILD / "submission.json").read_text(encoding="utf-8"))
    for record in submission:
        qid = int(record["id"])
        if qid > 361:
            continue
        for evidence in record["evidence"]:
            path = BUILD / evidence["csv_path"]
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            for row in rows:
                if "source_scale" not in row:
                    continue
                scale = float(row["source_scale"])
                context = " | ".join(
                    str(row.get(key, ""))
                    for key in ("column_header", "section", "table_context")
                )
                explicit_million = bool(
                    re.search(r"(?i)(tri[ệe]u\s*(?:đồng|vnd)|đvt\s*:\s*tri[ệe]u)", context)
                )
                explicit_thousand = bool(
                    re.search(r"(?i)(ngh[iì]n\s*(?:đồng|vnd)|đvt\s*:\s*ngh[iì]n)", context)
                )
                explicit_billion = bool(
                    re.search(r"(?i)(tỷ\s*(?:đồng|vnd)|đvt\s*:\s*tỷ)", context)
                )
                mismatch = (
                    (explicit_million and scale != 1_000_000.0)
                    or (explicit_thousand and scale != 1_000.0)
                    or (explicit_billion and scale != 1_000_000_000.0)
                )
                requested = float(row.get("requested_scale") or 1.0)
                raw_number = abs(float(row.get("raw_number") or 0.0))
                bank_tickers = {
                    "ACB", "BAB", "BID", "CTG", "EIB", "HDB", "KLB", "MBB", "MSB",
                    "NAB", "NVB", "OCB", "SHB", "STB", "TCB", "TPB", "VCB", "VIB", "VPB",
                }
                small_unscaled_million = (
                    requested == 1_000_000.0
                    and scale == 1.0
                    and 1_000.0 <= raw_number < 1_000_000_000.0
                )
                bank_unscaled_million = (
                    requested == 1_000_000.0
                    and scale == 1.0
                    and str(row.get("ticker")) in bank_tickers
                )
                if mismatch or small_unscaled_million or bank_unscaled_million:
                    print(
                        f"Q{qid} answer={record['answer']} source_scale={scale:g} "
                        f"requested_scale={row.get('requested_scale')} raw={row.get('raw_value')}\n"
                        f"  {record['question']}\n"
                        f"  {row.get('doc_id')} T{row.get('table_id')} R{row.get('row_idx')}C{row.get('col_idx')} "
                        f"label={row.get('row_label')} header={row.get('column_header')}\n"
                        f"  context={str(row.get('table_context', ''))[:240]}"
                    )


if __name__ == "__main__":
    main()
