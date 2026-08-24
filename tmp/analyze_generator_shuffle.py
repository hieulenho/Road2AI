"""Test whether Easy question IDs leak the seed-42 source-table order."""

from __future__ import annotations

import json
import random
import sqlite3
import sys
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import load_questions  # noqa: E402
from road2ai_vifinqa.easy_solver import EASY_AUDITED_OVERRIDES  # noqa: E402
from road2ai_vifinqa.paths import INDEX_PATH  # noqa: E402


OUTPUT = ROOT / "runs" / "live_search" / "generator_shuffle_analysis.json"


def main() -> None:
    connection = sqlite3.connect(f"file:{INDEX_PATH.as_posix()}?mode=ro", uri=True)
    docs = list(
        connection.execute(
            "SELECT doc_id,ticker,report_year FROM documents "
            "ORDER BY ticker,report_year,doc_id"
        )
    )
    candidates: list[tuple[str, int]] = []
    for doc_id, _ticker, _year in docs:
        table_ids = [
            int(row[0])
            for row in connection.execute(
                "SELECT table_id FROM tables WHERE doc_id=? ORDER BY table_id", (doc_id,)
            )
        ]
        candidates.extend((str(doc_id), table_id) for table_id in table_ids)
    random.Random(42).shuffle(candidates)
    position = {key: index for index, key in enumerate(candidates, 1)}
    questions = {int(row["id"]): str(row["question"]) for row in load_questions()}
    rows: list[dict[str, object]] = []
    for qid, (_operation, coordinates, _reason) in sorted(EASY_AUDITED_OVERRIDES.items()):
        tables = list(dict.fromkeys((doc_id, int(table_id)) for doc_id, table_id, _row, _col in coordinates))
        positions = [position[table] for table in tables]
        rows.append(
            {
                "id": qid,
                "question": questions[qid],
                "tables": [f"{doc}|{table_id}" for doc, table_id in tables],
                "positions": positions,
                "minimum_position": min(positions),
            }
        )
    qids = np.asarray([int(row["id"]) for row in rows], dtype=float)
    positions = np.asarray([int(row["minimum_position"]) for row in rows], dtype=float)
    spearman = spearmanr(qids, positions)
    kendall = kendalltau(qids, positions)
    ordered = sorted(rows, key=lambda row: int(row["id"]))
    monotone_pairs = sum(
        int(ordered[index]["minimum_position"]) > int(ordered[index - 1]["minimum_position"])
        for index in range(1, len(ordered))
    )
    payload = {
        "schema": 1,
        "candidate_count": len(candidates),
        "audited_count": len(rows),
        "spearman": {"statistic": float(spearman.statistic), "pvalue": float(spearman.pvalue)},
        "kendall": {"statistic": float(kendall.statistic), "pvalue": float(kendall.pvalue)},
        "adjacent_monotone_fraction": monotone_pairs / max(len(ordered) - 1, 1),
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
