import json
import re
import sqlite3
import sys
import zipfile
from pathlib import Path


TABLE_RE = re.compile(br"<table\b[^>]*>.*?</table>", re.I | re.S)
ROW_RE = re.compile(br"<tr\b", re.I)


doc_id = sys.argv[1]
table_id = int(sys.argv[2])
connection = sqlite3.connect("artifacts/tables.sqlite3")
source_path, table_count = connection.execute(
    "SELECT source_path, table_count FROM documents WHERE doc_id=?", (doc_id,)
).fetchone()
raw = Path(source_path).read_bytes()
blocks = list(TABLE_RE.finditer(raw))
assert len(blocks) == table_count
delta = 0
positions = []
physical_positions = []
for zero_id, block in enumerate(blocks):
    physical_zero = raw.count(b"\n", 0, block.start())
    physical_positions.append(physical_zero)
    expanded_zero = physical_zero + delta
    positions.append(expanded_zero)
    row_count = len(ROW_RE.findall(block.group(0)))
    physical_span = block.group(0).count(b"\n") + 1
    delta += max(1, row_count) - physical_span
print(json.dumps({"doc_id": doc_id, "table_id": table_id, "zero_index": table_id - 1, "physical_zero": physical_positions[table_id - 1], "expanded_zero": positions[table_id - 1]}))
for zero_id, position in enumerate(positions):
    if position == 1178:
        print(json.dumps({"expanded_zero": 1178, "source_table_id": zero_id + 1}))
for zero_id, position in enumerate(physical_positions):
    if position == 1178:
        print(json.dumps({"physical_zero": 1178, "source_table_id": zero_id + 1}))

with zipfile.ZipFile("submission_vn53.zip") as archive:
    rows = json.loads(archive.read("submission.json"))
for row in rows:
    if int(row["id"]) == 22:
        print(json.dumps({"q22_current_tables": row["relevant_tables"]}))
