"""Read-only evidence-vs-retrieval table coverage diagnostic."""

from __future__ import annotations

import csv
import io
import json
import statistics
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.submission import canonical_table_ref


def main() -> None:
    with zipfile.ZipFile(ROOT / "submission_vn75.zip") as archive:
        rows = json.loads(archive.read("submission.json"))
        diagnostics = []
        for row in rows:
            evidence_refs = set()
            for evidence in row["evidence"]:
                data = archive.read(evidence["csv_path"]).decode("utf-8")
                for source in csv.DictReader(io.StringIO(data)):
                    doc_id = source.get("doc_id")
                    table_id = source.get("table_id")
                    if doc_id and table_id and table_id.strip():
                        evidence_refs.add(canonical_table_ref(f"{doc_id}|table_{int(float(table_id))}"))
            retrieval = set(row["relevant_tables"])
            diagnostics.append({
                "id": row["id"],
                "retrieval": len(retrieval),
                "evidence": len(evidence_refs),
                "intersection": len(retrieval & evidence_refs),
                "missing_evidence": sorted(evidence_refs - retrieval),
                "extra": len(retrieval - evidence_refs),
            })
    payload = {
        "rows": len(diagnostics),
        "retrieval_mean": statistics.mean(item["retrieval"] for item in diagnostics),
        "evidence_mean": statistics.mean(item["evidence"] for item in diagnostics),
        "intersection_mean": statistics.mean(item["intersection"] for item in diagnostics),
        "extra_total": sum(item["extra"] for item in diagnostics),
        "missing_evidence_total": sum(len(item["missing_evidence"]) for item in diagnostics),
        "coverage_full": sum(not item["missing_evidence"] for item in diagnostics),
        "by_retrieval": Counter(item["retrieval"] for item in diagnostics),
        "largest_extra": sorted(diagnostics, key=lambda item: (-item["extra"], -item["retrieval"]))[:40],
        "missing_evidence": [item for item in diagnostics if item["missing_evidence"]][:80],
    }
    (ROOT / "runs" / "reasoning_selector" / "vn75_evidence_table_coverage.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
