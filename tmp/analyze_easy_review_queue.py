from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.easy_solver import EASY_AUDITED_OVERRIDES  # noqa: E402


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    queue = json.loads(
        (ROOT / "runs/agent_easy_resolver_cv/unoverridden_review_queue.json").read_text(
            encoding="utf-8"
        )
    )
    baseline = json.loads(
        (ROOT / "tmp/vn53_analysis_20260824/submission.json").read_text(encoding="utf-8")
    )
    by_id = {int(row["id"]): row for row in baseline}

    rows = []
    for item in queue:
        qid = int(item["id"])
        if qid in EASY_AUDITED_OVERRIDES:
            continue
        top = item.get("top") or {}
        current = (item.get("current") or [{}])[0]
        old = float(by_id[qid]["answer"])
        new = top.get("answer_value")
        if new is None or abs(float(new) - old) <= max(1e-9, abs(old) * 1e-12):
            continue
        rows.append(
            (
                float(item.get("confidence", 0.0)),
                float(item.get("score_margin_over_current", 0.0)),
                qid,
                item["question"],
                old,
                float(new),
                top.get("doc_id"),
                top.get("table_id"),
                top.get("row_idx"),
                top.get("col_idx"),
                top.get("row_label"),
                top.get("column_header"),
                current.get("doc_id"),
                current.get("table_id"),
                current.get("row_idx"),
                current.get("col_idx"),
                current.get("row_label"),
                current.get("column_header"),
            )
        )

    rows.sort(reverse=True)
    print(f"audited={len(EASY_AUDITED_OVERRIDES)} candidates={len(rows)}")
    for row in rows:
        (
            confidence,
            margin,
            qid,
            question,
            old,
            new,
            tdoc,
            ttable,
            trow,
            tcol,
            tlabel,
            theader,
            cdoc,
            ctable,
            crow,
            ccol,
            clabel,
            cheader,
        ) = row
        print(
            f"\nQ{qid} conf={confidence:.3f} margin={margin:.3f} old={old:g} new={new:g}\n"
            f"  {question}\n"
            f"  TOP {tdoc} t{ttable} r{trow} c{tcol} [{theader}] {tlabel}\n"
            f"  CUR {cdoc} t{ctable} r{crow} c{ccol} [{cheader}] {clabel}"
        )


if __name__ == "__main__":
    main()
