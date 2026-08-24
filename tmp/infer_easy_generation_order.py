from __future__ import annotations

import argparse
import random
import sqlite3
from pathlib import Path

from road2ai_vifinqa.easy_solver import EASY_AUDITED_OVERRIDES


def rank_correlation(xs: list[int], ys: list[int]) -> float:
    def ranks(values: list[int]) -> list[int]:
        order = sorted(range(len(values)), key=values.__getitem__)
        result = [0] * len(values)
        for rank, index in enumerate(order):
            result[index] = rank
        return result

    rx = ranks(xs)
    ry = ranks(ys)
    n = len(xs)
    mean = (n - 1) / 2
    numerator = sum((a - mean) * (b - mean) for a, b in zip(rx, ry, strict=True))
    denominator = sum((a - mean) ** 2 for a in rx) ** 0.5 * sum(
        (b - mean) ** 2 for b in ry
    ) ** 0.5
    return numerator / denominator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=Path("artifacts/tables_v2.sqlite3"))
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--seed-stop", type=int, default=43)
    args = parser.parse_args()

    with sqlite3.connect(args.index) as connection:
        candidates = [
            (str(doc_id), int(table_id))
            for doc_id, table_id in connection.execute(
                "SELECT doc_id, table_id FROM tables ORDER BY doc_id, table_id"
            )
        ]
    target = {
        qid: (spec[1][0][0], spec[1][0][1])
        for qid, spec in EASY_AUDITED_OVERRIDES.items()
        if len(spec[1]) == 1
    }
    candidate_set = set(candidates)
    target = {qid: key for qid, key in target.items() if key in candidate_set}
    qids = sorted(target)
    results: list[tuple[float, int, int, int]] = []
    for seed in range(args.seed_start, args.seed_stop):
        shuffled = list(candidates)
        random.Random(seed).shuffle(shuffled)
        positions = {key: index for index, key in enumerate(shuffled)}
        source_positions = [positions[target[qid]] for qid in qids]
        rho = rank_correlation(qids, source_positions)
        forward = sum(
            source_positions[index] < source_positions[index + 1]
            for index in range(len(source_positions) - 1)
        )
        first_span = max(source_positions[:10]) if len(source_positions) >= 10 else 0
        results.append((rho, forward, -first_span, seed))
    for rho, forward, neg_span, seed in sorted(results, reverse=True)[:20]:
        print(
            f"seed={seed} rho={rho:.6f} adjacent_forward={forward}/{len(qids)-1} "
            f"first10_max_rank={-neg_span} targets={len(qids)} candidates={len(candidates)}"
        )


if __name__ == "__main__":
    main()
