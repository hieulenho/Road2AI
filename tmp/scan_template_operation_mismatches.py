from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data/source/ViFinQA/questions/questions.jsonl"
CHECKPOINTS = ROOT / "runs/live_search/template_current/checkpoints"


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.casefold())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text)


def expected_ops(question: str) -> set[str]:
    q = fold(question)
    if "nam nao" in q:
        return {"argmin"} if any(x in q for x in ("thap nhat", "nho nhat")) else {"argmax"}
    if re.search(r"\b(?:bao nhieu nam|bao nhieu cong ty|tong so cong ty|so cong ty co)\b", q):
        return {"count"}
    if re.search(r"(?:cao nhat|lon nhat) (?:la |bang )?bao nhieu", q):
        return {"maximum"}
    if re.search(r"(?:thap nhat|nho nhat) (?:la |bang )?bao nhieu", q):
        return {"minimum"}
    if "trung binh" in q:
        return {"mean"}
    # "bình quân" is frequently part of a source-row label.  Only treat it as
    # a reducer when the question explicitly asks for the mean of several
    # entities/years.
    if "binh quan" in q and any(x in q for x in ("cua cac", "giua cac", "trong giai doan", "trong cac nam")):
        return {"mean"}
    if any(x in q for x in ("toc do tang", "tang truong", "ty le tang", "ty suat tang")):
        return {"growth"}
    if any(x in q for x in ("chenh lech", "hieu so", "hieu giua", "tru di", "lon hon", "be hon", "kem hon")):
        return {"difference"}
    if any(x in q for x in ("ty le", "ty trong", "ty suat", "ty so", "bao nhieu lan", "bien loi nhuan")):
        return {"ratio"}
    if re.search(r"\b(?:tong cong|tong gia tri|tong cua|cong lai)\b", q):
        return {"sum"}
    return {"value"}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    questions = {}
    with QUESTIONS.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            questions[int(item["id"])] = item["question"]

    mismatches = []
    for qid in range(578, 1013):
        path = CHECKPOINTS / f"q{qid:04d}.json"
        if not path.exists():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        method = str(record.get("method", ""))
        actual = method.split(":", 1)[1] if ":" in method else method
        expected = expected_ops(questions[qid])
        # Difference families sometimes contain ratios as operands, but their
        # top-level operation must remain difference.
        if actual not in expected:
            mismatches.append(
                {
                    "qid": qid,
                    "actual": actual,
                    "expected": sorted(expected),
                    "answer": record.get("answer"),
                    "question": questions[qid],
                }
            )

    out = ROOT / "runs/live_search/template_operation_mismatches.json"
    out.write_text(json.dumps(mismatches, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"mismatches={len(mismatches)} output={out}")
    for item in mismatches:
        print(
            f"Q{item['qid']} current={item['actual']} expected={','.join(item['expected'])} "
            f"answer={item['answer']}\n  {item['question']}"
        )


if __name__ == "__main__":
    main()
