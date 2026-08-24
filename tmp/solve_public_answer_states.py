from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "runs/live_search/public_answer_state_equations.json"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    alt_vars = payload["variables"]

    states_by_qid: dict[int, set[str]] = defaultdict(set)
    for var in alt_vars:
        states_by_qid[int(var["qid"])].add(str(var["answer_state"]))

    # Recover each VN53 base state from a submission equation variable's qid by
    # reading the organizer-ready package.
    import zipfile

    with zipfile.ZipFile(ROOT / payload["base"]) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".json"))
        rows = json.loads(archive.read(name).decode("utf-8"))
    base_state = {int(row["id"]): f"{float(row['answer']):.12g}" for row in rows}
    for qid in list(states_by_qid):
        states_by_qid[qid].add(base_state[qid])

    state_vars = {}
    for qid in sorted(states_by_qid):
        for state in sorted(states_by_qid[qid]):
            state_vars[(qid, state)] = len(state_vars)

    eqs = payload["equations"]
    matrix = lil_matrix((len(eqs), len(state_vars)), dtype=float)
    rhs = np.zeros(len(eqs), dtype=float)
    alt_lookup = {int(var["index"]): var for var in alt_vars}
    for row_idx, equation in enumerate(eqs):
        rhs[row_idx] = float(equation["rhs"])
        for old_idx_raw, coefficient in equation["coeffs"].items():
            var = alt_lookup[int(old_idx_raw)]
            qid = int(var["qid"])
            alt = str(var["answer_state"])
            base = base_state[qid]
            matrix[row_idx, state_vars[(qid, alt)]] += float(coefficient)
            matrix[row_idx, state_vars[(qid, base)]] -= float(coefficient)

    constraints = LinearConstraint(matrix.tocsr(), rhs, rhs)
    bounds = Bounds(np.zeros(len(state_vars)), np.ones(len(state_vars)))
    integrality = np.ones(len(state_vars), dtype=int)
    zero = np.zeros(len(state_vars), dtype=float)
    feasible = milp(zero, integrality=integrality, bounds=bounds, constraints=constraints)
    if not feasible.success:
        raise RuntimeError(feasible.message)

    results = []
    for qid in sorted(states_by_qid):
        base = base_state[qid]
        for alt in sorted(states_by_qid[qid]):
            if alt == base:
                continue
            objective = np.zeros(len(state_vars), dtype=float)
            objective[state_vars[(qid, alt)]] = 1.0
            objective[state_vars[(qid, base)]] = -1.0
            minimum = milp(
                objective,
                integrality=integrality,
                bounds=bounds,
                constraints=constraints,
                options={"time_limit": 10},
            )
            maximum = milp(
                -objective,
                integrality=integrality,
                bounds=bounds,
                constraints=constraints,
                options={"time_limit": 10},
            )
            if not minimum.success or not maximum.success:
                raise RuntimeError(f"MILP failed for Q{qid}")
            lo = int(round(minimum.fun))
            hi = int(round(-maximum.fun))
            results.append({"qid": qid, "base": base, "alt": alt, "delta_min": lo, "delta_max": hi})

    out = ROOT / "runs/live_search/public_answer_state_inference.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    fixed = [item for item in results if item["delta_min"] == item["delta_max"]]
    print(
        f"state_variables={len(state_vars)} equations={len(eqs)} "
        f"alternates={len(results)} fixed={len(fixed)} output={out}"
    )
    print("\n=== Proven deltas versus VN53 ===")
    for item in fixed:
        print(f"Q{item['qid']}: {item['base']} -> {item['alt']} delta={item['delta_min']:+d}")
    print("\n=== Ambiguous alternates (possible improvement first) ===")
    for item in sorted(
        (item for item in results if item not in fixed),
        key=lambda item: (-item["delta_max"], item["delta_min"], item["qid"]),
    ):
        print(
            f"Q{item['qid']}: {item['base']} -> {item['alt']} "
            f"delta=[{item['delta_min']:+d},{item['delta_max']:+d}]"
        )


if __name__ == "__main__":
    main()
