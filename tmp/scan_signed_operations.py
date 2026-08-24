from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYS = (
    "chênh lệch",
    "cao hơn",
    "thấp hơn",
    "nhiều hơn",
    "ít hơn",
    "vượt",
    "kém hơn",
    "trừ đi",
    "thay đổi",
    "biến động",
    "tăng",
    "giảm",
)


with zipfile.ZipFile(ROOT / "submission_vn53.zip") as archive:
    rows = json.loads(archive.read("submission.json").decode("utf-8"))

for row in rows:
    question = str(row["question"])
    folded = question.lower()
    if not any(key in folded for key in KEYS):
        continue
    query = str(row["pandas_query"])
    kind = "abs" if "abs(" in query else "sub" if "-" in query else "other"
    print(f"{int(row['id']):4d}\t{kind:5s}\t{float(row['answer']):.12g}\t{question}")
