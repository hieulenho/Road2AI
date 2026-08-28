import json
import re
import sys
import unicodedata
import zipfile
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from road2ai_vifinqa.corpus import load_questions  # noqa: E402


def fold(text):
    text = str(text).replace("đ", "d").replace("Đ", "D").lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(re.findall(r"[a-z0-9]+", text))


questions = load_questions()
with zipfile.ZipFile(ROOT / "submission_vn53.zip") as archive:
    name = next(name for name in archive.namelist() if name.endswith(".json"))
    answers = {int(row["id"]): float(row["answer"]) for row in json.loads(archive.read(name))}

rows = []
for row in questions:
    qid = int(row["id"])
    question = str(row["question"])
    normalized = fold(question)
    tokens = set(normalized.split())
    tickers = tuple(sorted(set(re.findall(r"\b[A-Z]{2,5}\b", question))))
    years = tuple(sorted(set(re.findall(r"\b20\d{2}\b", question))))
    rows.append((qid, question, normalized, tokens, tickers, years))

# Inverted rare-token index avoids scoring all half-million pairs.
index = defaultdict(list)
for position, row in enumerate(rows):
    for token in row[3]:
        if len(token) >= 4:
            index[token].append(position)

pairs = set()
for postings in index.values():
    if len(postings) > 120:
        continue
    for offset, left in enumerate(postings):
        for right in postings[offset + 1 :]:
            pairs.add((left, right))

results = []
for left, right in pairs:
    a, b = rows[left], rows[right]
    if a[4] != b[4] or a[5] != b[5]:
        continue
    intersection = len(a[3] & b[3])
    union = len(a[3] | b[3])
    jaccard = intersection / union if union else 0.0
    if jaccard < 0.72:
        continue
    ratio = SequenceMatcher(None, a[2], b[2], autojunk=False).ratio()
    if ratio < 0.80:
        continue
    av, bv = answers[a[0]], answers[b[0]]
    same_answer = abs(av - bv) <= 1e-9 * max(1.0, abs(av), abs(bv))
    results.append({
        "left": a[0], "right": b[0], "jaccard": jaccard, "ratio": ratio,
        "left_answer": av, "right_answer": bv, "same_answer": same_answer,
        "left_question": a[1], "right_question": b[1],
    })

results.sort(key=lambda item: (item["same_answer"], -item["jaccard"], -item["ratio"]))
Path(ROOT / "runs/live_search/semantic_duplicate_disagreements.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
for item in results[:120]:
    if item["same_answer"]:
        continue
    print(
        f"Q{item['left']}/Q{item['right']} j={item['jaccard']:.3f} r={item['ratio']:.3f} "
        f"ans={item['left_answer']} vs {item['right_answer']}"
    )
    print(" ", item["left_question"])
    print(" ", item["right_question"])
print("pairs", len(pairs), "matched", len(results), "disagreed", sum(not x["same_answer"] for x in results))
