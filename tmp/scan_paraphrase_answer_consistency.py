from __future__ import annotations

import json
import math
import re
from difflib import SequenceMatcher
from pathlib import Path

from road2ai_vifinqa.corpus import Corpus
from road2ai_vifinqa.text import fold_text


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tmp" / "vn53_analysis_20260824"
RECORDS = json.loads((EXTRACT / "submission.json").read_text(encoding="utf-8"))

STOP = {
    "cua", "la", "bao", "nhieu", "trong", "tai", "vao", "nam", "cac", "cong", "ty",
    "co", "phan", "tap", "doan", "tong", "va", "tu", "den", "voi", "theo", "don", "vi",
    "tinh", "gia", "tri", "muc", "so", "du", "cuoi", "dau", "cho", "biet", "nhom", "xet",
}


def tokens(question: str) -> frozenset[str]:
    values = re.findall(r"[a-z0-9]+", fold_text(question))
    return frozenset(value for value in values if value not in STOP and len(value) > 1)


def relative_gap(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), 1e-12)


items: list[dict[str, object]] = []
with Corpus() as corpus:
    for record in RECORDS:
        question = str(record["question"])
        items.append(
            {
                "qid": int(record["id"]),
                "question": question,
                "folded": fold_text(question),
                "tokens": tokens(question),
                "tickers": tuple(sorted(corpus.infer_tickers(question))),
                "years": tuple(sorted(corpus.infer_years(question))),
                "answer": float(record["answer"]),
            }
        )

pairs: list[dict[str, object]] = []
for index, left in enumerate(items):
    for right in items[index + 1 :]:
        if left["tickers"] != right["tickers"] or left["years"] != right["years"]:
            continue
        left_tokens = left["tokens"]
        right_tokens = right["tokens"]
        union = left_tokens | right_tokens
        jaccard = len(left_tokens & right_tokens) / max(len(union), 1)
        if jaccard < 0.52:
            continue
        sequence = SequenceMatcher(None, left["folded"], right["folded"]).ratio()
        if max(jaccard, sequence) < 0.70:
            continue
        gap = relative_gap(float(left["answer"]), float(right["answer"]))
        pairs.append(
            {
                "left_qid": left["qid"],
                "right_qid": right["qid"],
                "jaccard": jaccard,
                "sequence": sequence,
                "answer_gap": gap,
                "left_answer": left["answer"],
                "right_answer": right["answer"],
                "tickers": left["tickers"],
                "years": left["years"],
                "left_question": left["question"],
                "right_question": right["question"],
            }
        )

pairs.sort(key=lambda item: (-float(item["jaccard"]), -float(item["sequence"]), -float(item["answer_gap"])))
path = ROOT / "runs" / "live_search" / "paraphrase_answer_consistency_scan.json"
path.write_text(json.dumps(pairs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for item in pairs[:250]:
    print(
        f"Q{item['left_qid']}/Q{item['right_qid']} jac={item['jaccard']:.3f} "
        f"seq={item['sequence']:.3f} gap={item['answer_gap']:.4g} "
        f"answers={item['left_answer']}/{item['right_answer']} tickers={item['tickers']} years={item['years']}"
    )
    print(f"  L {item['left_question']}")
    print(f"  R {item['right_question']}")
