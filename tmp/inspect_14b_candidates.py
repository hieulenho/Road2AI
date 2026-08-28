import json
import zipfile
from pathlib import Path

from road2ai_vifinqa.corpus import Corpus


QIDS = {102, 164, 178, 237, 357}
RESULT_FILES = [
    Path("runs/live_search/easy_14b_risk_results.json"),
    Path("runs/live_search/easy_14b_batch2_results.json"),
    Path("runs/live_search/easy_q4_benchmark_results.json"),
]

with zipfile.ZipFile("submission_vn53.zip") as archive:
    baseline = {
        int(row["id"]): row
        for row in json.loads(archive.read("submission.json").decode("utf-8"))
    }

alts = {}
for path in RESULT_FILES:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for key, result in payload.get("rows", {}).items():
        qid = int(key)
        if qid in QIDS and not result.get("error") and result.get("selected"):
            alts[qid] = result["selected"][0]

with Corpus() as corpus:
    for qid in sorted(QIDS):
        row = baseline[qid]
        selected = alts[qid]
        table = corpus.table(selected["doc_id"], int(selected["table_id"]))
        print("\n" + "=" * 100)
        print(f"Q{qid}: {row['question']}")
        print(f"BASE answer={row['answer']} tables={row['relevant_tables']}")
        print(f"BASE evidence={row['evidence']} query={row['pandas_query']}")
        print(
            f"ALT answer={selected.get('answer_value')} {selected['doc_id']}|{selected['table_id']} "
            f"r{selected['row_idx']}c{selected['col_idx']} raw={selected['raw_value']} "
            f"row={selected.get('row_label')} header={selected.get('column_header')}"
        )
        print(f"TABLE context={table.context!r} kind={table.statement_kind} scale={table.unit_scale}")
        lo = max(0, int(selected["row_idx"]) - 5)
        hi = min(len(table.rows), int(selected["row_idx"]) + 6)
        for idx in range(lo, hi):
            marker = ">>>" if idx == int(selected["row_idx"]) else "   "
            print(f"{marker} r{idx}: {table.rows[idx]}")
