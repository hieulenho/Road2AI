import json
from pathlib import Path


records = json.loads(
    Path("runs/live_search/paraphrase_answer_consistency_scan.json").read_text(
        encoding="utf-8"
    )
)

for record in records:
    if record["answer_gap"] <= 1e-12:
        continue
    print(
        f"Q{record['left_qid']}/Q{record['right_qid']} "
        f"gap={record['answer_gap']:.6g} sim={record['sequence']:.3f}"
    )
    print(f" L={record['left_answer']} | {record['left_question']}")
    print(f" R={record['right_answer']} | {record['right_question']}")
    print()
