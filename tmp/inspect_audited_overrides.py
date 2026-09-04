"""Compare source-audited Easy overrides against the current release.

Diagnostic only: this writes no release artifact and never uses leaderboard
scores as labels.
"""

from __future__ import annotations

import json
import math
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus, load_questions
from road2ai_vifinqa.easy_solver import (
    EASY_AUDITED_OVERRIDES,
    _audited_override_solution,
)
from road2ai_vifinqa.easy_solver import build_easy_candidates


def main() -> None:
    with zipfile.ZipFile(ROOT / "submission_vn74.zip") as archive:
        rows = {int(row["id"]): row for row in json.loads(archive.read("submission.json"))}
    questions = {int(row["id"]): str(row["question"]) for row in load_questions()}
    differences = []
    with Corpus() as corpus:
        for qid in sorted(EASY_AUDITED_OVERRIDES):
            candidates = build_easy_candidates(corpus, questions[qid])
            solution = _audited_override_solution(
                qid, candidates, shortlisted_candidates=len(candidates), started=0.0,
            )
            assert solution is not None
            current = float(rows[qid]["answer"])
            proposed = float(solution.answer)
            if not math.isclose(current, proposed, rel_tol=1e-12, abs_tol=1e-9):
                differences.append({
                    "id": qid,
                    "question": questions[qid],
                    "current": current,
                    "proposed": proposed,
                    "operation": EASY_AUDITED_OVERRIDES[qid][0],
                    "reason": EASY_AUDITED_OVERRIDES[qid][2],
                    "sources": [
                        {
                            "doc_id": source.doc_id,
                            "table_id": source.table_id,
                            "row_idx": source.row_idx,
                            "col_idx": source.col_idx,
                            "source_scale": source.source_scale,
                            "raw": source.raw_number,
                            "value": source.answer_value,
                        }
                        for source in solution.selected
                    ],
                })
    payload = {
        "override_count": len(EASY_AUDITED_OVERRIDES),
        "different_count": len(differences),
        "differences": differences,
    }
    (ROOT / "runs" / "reasoning_selector" / "vn75_audited_override_diff.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
