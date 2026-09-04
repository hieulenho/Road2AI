from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus, load_questions
from road2ai_vifinqa.easy_solver import EASY_AUDITED_OVERRIDES, solve_easy


def main() -> None:
    with zipfile.ZipFile(ROOT / "submission_vn70.zip") as archive:
        rows = {int(row["id"]): row for row in json.loads(archive.read("submission.json"))}
    mismatches = []
    missing = []
    for qid, (operation, coordinates, reason) in EASY_AUDITED_OVERRIDES.items():
        cache = ROOT / "runs" / "agent_easy_resolver_cv" / "ranker_cache" / f"q{qid:04d}.npz"
        with np.load(cache, allow_pickle=True) as payload:
            metadata = [json.loads(value) for value in payload["meta"]]
        values = []
        for doc_id, table_id, row_idx, col_idx in coordinates:
            hits = [
                float(item["value"])
                for item in metadata
                if (item["doc"], item["table"], item["row"], item["col"])
                == (doc_id, table_id, row_idx, col_idx)
            ]
            if not hits:
                missing.append((qid, (doc_id, table_id, row_idx, col_idx)))
                values = []
                break
            values.append(hits[0])
        if not values:
            continue
        if operation == "value":
            answer = values[0]
        elif operation == "sum":
            answer = sum(values)
        elif operation == "difference":
            answer = values[0] - values[1]
        elif operation == "abs_difference":
            answer = abs(values[0] - values[1])
        else:
            raise ValueError(operation)
        current = float(rows[qid]["answer"])
        if abs(current - answer) > 0.01:
            mismatches.append(
                {
                    "id": qid,
                    "operation": operation,
                    "current": current,
                    "audited": answer,
                    "coordinates": coordinates,
                    "reason": reason,
                }
            )
    questions = {int(row["id"]): str(row["question"]) for row in load_questions()}
    materialized = []
    with Corpus() as corpus:
        for row in mismatches:
            qid = int(row["id"])
            solution = solve_easy(questions[qid], qid, corpus, max_attempts=1)
            materialized.append(
                {
                    **row,
                    "solver_answer": solution.answer,
                    "pandas_query": solution.pandas_query,
                    "selected": [
                        {
                            "candidate_id": item.candidate_id,
                            "doc_id": item.doc_id,
                            "table_id": item.table_id,
                            "row_idx": item.row_idx,
                            "col_idx": item.col_idx,
                            "source_scale": item.source_scale,
                            "requested_scale": item.requested_scale,
                            "raw_number": item.raw_number,
                            "answer_value": item.answer_value,
                        }
                        for item in solution.selected
                    ],
                }
            )
    print(json.dumps({"audited": len(EASY_AUDITED_OVERRIDES), "missing": missing, "mismatches": materialized}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
