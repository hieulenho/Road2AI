from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from road2ai_vifinqa.corpus import Corpus


with Corpus() as corpus:
    for doc_id, table_id in (
        ("OGC_financial_statements_2019_consolidated", 5),
        ("OGC_financial_statements_2019_consolidated", 29),
        ("CEO_financial_statements_2022_consolidated", 51),
    ):
        table = corpus.table(doc_id, table_id)
        print(f"TABLE {table_id}\nCONTEXT\n{table.context}\nROWS")
        for index, row in enumerate(table.rows):
            print(index, row)
        print()
