"""Measure whether prompt serialization drops audited Easy gold cells.

Read-only diagnostic: it rebuilds the current production shortlist and compares
the 22k-character preview with a shorter semantic representation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus, load_questions
from road2ai_vifinqa.easy_solver import (
    EASY_AUDITED_OVERRIDES,
    _preview,
    build_easy_candidates,
    shortlist_easy_candidates,
)
from road2ai_vifinqa.retrieval import retrieve_rows


def _compact(candidates: list[object], limit: int = 22_000) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        item = {
            "id": candidate.candidate_id,
            "row_label": candidate.row_label[:112],
            "section": candidate.section[:88],
            "column_header": candidate.column_header[:96],
            "table_context": candidate.table_context[:130],
            "answer_value": candidate.answer_value,
            "rank_score": round(candidate.retrieval_score, 4),
        }
        if len(json.dumps([*rows, item], ensure_ascii=False, separators=(",", ":"))) > limit:
            break
        rows.append(item)
    return rows


def main() -> None:
    questions = {int(row["id"]): str(row["question"]) for row in load_questions()}
    records: list[dict[str, object]] = []
    with Corpus() as corpus:
        for ordinal, qid in enumerate(sorted(EASY_AUDITED_OVERRIDES), start=1):
            question = questions[qid]
            exhaustive = build_easy_candidates(corpus, question)
            hits = retrieve_rows(corpus, question, limit=100_000, include_prior=False)
            bm25 = {
                (hit.row.doc_id, hit.row.table_id, hit.row.row_idx): float(hit.score)
                for hit in hits
            }
            shortlist = shortlist_easy_candidates(
                exhaustive,
                question=question,
                bm25_row_scores=bm25,
                use_learned_reranker=True,
            )
            default = _preview(shortlist)
            compact = _compact(shortlist)
            by_id = {candidate.candidate_id: candidate for candidate in shortlist}
            coords = EASY_AUDITED_OVERRIDES[qid][1]
            gold_ids = [
                candidate.candidate_id
                for candidate in shortlist
                if (candidate.doc_id, candidate.table_id, candidate.row_idx, candidate.col_idx)
                in coords
            ]
            default_ids = {str(row["id"]) for row in default}
            compact_ids = {str(row["id"]) for row in compact}
            records.append(
                {
                    "id": qid,
                    "gold_ids_in_shortlist": gold_ids,
                    "shortlist_hit": bool(gold_ids),
                    "default_preview_hit": any(value in default_ids for value in gold_ids),
                    "compact_preview_hit": any(value in compact_ids for value in gold_ids),
                    "default_n": len(default),
                    "compact_n": len(compact),
                    "shortlist_n": len(shortlist),
                    "gold_default_rank": min(
                        (next(i + 1 for i, row in enumerate(default) if row["id"] == value)
                         for value in gold_ids if value in default_ids),
                        default=None,
                    ),
                    "gold_compact_rank": min(
                        (next(i + 1 for i, row in enumerate(compact) if row["id"] == value)
                         for value in gold_ids if value in compact_ids),
                        default=None,
                    ),
                }
            )
            print(f"{ordinal:3d}/101 q{qid:04d}", flush=True)
    def n(key: str) -> int:
        return sum(bool(row[key]) for row in records)
    payload = {
        "schema": 1,
        "description": "Current production v2 shortlist against actual prompt-preview serialization.",
        "summary": {
            "n": len(records),
            "shortlist_hit": n("shortlist_hit"),
            "default_preview_hit": n("default_preview_hit"),
            "compact_preview_hit": n("compact_preview_hit"),
            "shortlist_to_default_loss": n("shortlist_hit") - n("default_preview_hit"),
            "default_to_compact_gain": n("compact_preview_hit") - n("default_preview_hit"),
            "default_preview_n": {
                "min": min(int(row["default_n"]) for row in records),
                "max": max(int(row["default_n"]) for row in records),
                "mean": sum(int(row["default_n"]) for row in records) / len(records),
            },
            "compact_preview_n": {
                "min": min(int(row["compact_n"]) for row in records),
                "max": max(int(row["compact_n"]) for row in records),
                "mean": sum(int(row["compact_n"]) for row in records) / len(records),
            },
        },
        "affected": [
            row for row in records
            if row["shortlist_hit"] and not row["default_preview_hit"]
        ],
        "compact_gains": [
            row for row in records
            if not row["default_preview_hit"] and row["compact_preview_hit"]
        ],
        "records": records,
    }
    target = ROOT / "runs" / "agent_nonlinear_reranker" / "preview_coverage.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
