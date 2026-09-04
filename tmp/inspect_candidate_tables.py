from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus

TARGETS = (
    ("MPC_financial_statements_2021_consolidated", 10),
    ("MPC_financial_statements_2021_consolidated", 69),
    ("MBB_financial_statements_2020_consolidated", 85),
    ("MBB_financial_statements_2020_consolidated", 86),
    ("FPT_financial_statements_2024_consolidated", 9),
)

with Corpus() as corpus:
    for doc_id, table_id in TARGETS:
        table = corpus.table(doc_id, table_id)
        print(f"\n{doc_id} TABLE {table_id}\n{table.context}\n")
        for row_index, row in enumerate(table.rows):
            print(row_index, row)
