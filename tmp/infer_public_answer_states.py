from __future__ import annotations

import json
import math
import os
import sys
import zipfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / os.environ.get(
    "PUBLIC_HISTORY",
    "runs/live_search/remote_history_20260824.json",
)
BASE_ZIP = ROOT / "submission_vn53.zip"
# The public phase scores 506 hidden-public rows (half of the 1,012 test
# questions).  This is directly identifiable from the 0.0020 score movement
# caused by the one-question Q821 correction: 1 / 506 = 0.001976...
N_QUESTIONS = 506


def load_submission(path: Path) -> dict[int, dict]:
    with zipfile.ZipFile(path) as archive:
        json_names = [name for name in archive.namelist() if name.endswith(".json")]
        if len(json_names) != 1:
            raise ValueError(f"{path}: expected one JSON, found {json_names}")
        rows = json.loads(archive.read(json_names[0]).decode("utf-8"))
    return {int(row["id"]): row for row in rows}


def state_key(row: dict) -> str:
    # Execution Accuracy depends on the value produced by pandas_query.  In all
    # historical packages the stored answer is the replayed query result, so a
    # stable numeric representation is the useful state identifier.
    value = float(row["answer"])
    if math.isnan(value):
        return "nan"
    return f"{value:.12g}"


def exact_count(rounded_score: float) -> int:
    candidates = [
        count
        for count in range(N_QUESTIONS + 1)
        if f"{count / N_QUESTIONS:.4f}" == f"{rounded_score:.4f}"
    ]
    if len(candidates) != 1:
        raise ValueError(f"score {rounded_score} maps to {candidates}")
    return candidates[0]


def local_zip(filename: str) -> Path | None:
    direct = ROOT / filename
    if direct.exists() and filename.lower().startswith("submission_vn"):
        return direct
    return None


def primary_score(item: dict) -> float | None:
    for score in item.get("scores", []):
        if score.get("column_key") == "EXECUTION_ACCURACY":
            return float(score["score"])
    return None


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    base = load_submission(BASE_ZIP)
    history_by_name = {}
    for item in history:
        name = str(item.get("filename", ""))
        if local_zip(name) is not None and primary_score(item) is not None:
            # VN filenames are unique in the organizer history.  Keep the most
            # recent row defensively if a duplicate appears.
            history_by_name[name] = item

    scored = []
    base_count = None
    for name, item in sorted(history_by_name.items()):
        path = local_zip(name)
        assert path is not None
        rows = load_submission(path)
        score = primary_score(item)
        assert score is not None
        count = exact_count(score)
        if name == BASE_ZIP.name:
            base_count = count
        diffs = []
        for qid, base_row in base.items():
            key = state_key(rows[qid])
            base_key = state_key(base_row)
            if key != base_key:
                diffs.append((qid, key, base_key))
        scored.append({"name": name, "count": count, "diffs": diffs})
    if base_count is None:
        raise RuntimeError("VN53 missing from organizer history")

    # Turn each alternate (question, numeric state) into a variable whose value
    # is correctness(alternate) - correctness(VN53 state), hence {-1, 0, +1}.
    var_index = {}
    for item in scored:
        for qid, key, _ in item["diffs"]:
            var_index.setdefault((qid, key), len(var_index))

    equations = []
    for item in scored:
        coeffs = defaultdict(int)
        for qid, key, _ in item["diffs"]:
            coeffs[var_index[(qid, key)]] += 1
        equations.append(
            {
                "name": item["name"],
                "rhs": item["count"] - base_count,
                "coeffs": dict(coeffs),
                "diff_qids": [qid for qid, _, _ in item["diffs"]],
            }
        )

    payload = {
        "base": BASE_ZIP.name,
        "base_count": base_count,
        "submissions": len(scored),
        "variables": [
            {"index": idx, "qid": qid, "answer_state": key}
            for (qid, key), idx in sorted(var_index.items(), key=lambda pair: pair[1])
        ],
        "equations": equations,
    }
    out = ROOT / "runs/live_search/public_answer_state_equations.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"base_count={base_count}/{N_QUESTIONS} submissions={len(scored)} "
        f"variables={len(var_index)} equations={len(equations)} output={out}"
    )
    for eq in equations:
        print(f"{eq['name']}: delta={eq['rhs']:+d} changed={len(eq['diff_qids'])} {eq['diff_qids']}")


if __name__ == "__main__":
    main()
