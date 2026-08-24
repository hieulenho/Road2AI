from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    return json.loads((ROOT / "runs/live_search" / name).read_text(encoding="utf-8"))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for name in [
        "template_ratio_homology_scan.json",
        "template_metric_alignment_scan.json",
        "template_period_section_scan.json",
    ]:
        print(f"\n=== {name} ===")
        for item in load(name)[:80]:
            labels = item.get("numerator_labels") or item.get("labels") or []
            den = item.get("denominator_labels") or []
            scores = item.get("scores") or []
            print(
                f"Q{item['qid']} ans={item.get('answer')} op={item.get('operation')} "
                f"score={item.get('min_score', item.get('risk_score', ''))} "
                f"labels={labels} den={den} scores={scores}\n  {item['question']}"
            )


if __name__ == "__main__":
    main()
