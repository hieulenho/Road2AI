import sqlite3,json
c=sqlite3.connect('file:artifacts/tables.sqlite3?mode=ro',uri=True)
for tid,ri in [(8,9),(8,19),(62,2)]:
 row=c.execute('select cells_json from rows where doc_id=? and table_id=? and row_idx=?',('PLX_financial_statements_2024_consolidated',tid,ri)).fetchone()
 print(tid,ri,row[0])
