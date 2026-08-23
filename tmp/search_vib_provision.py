import sqlite3
c=sqlite3.connect('file:artifacts/tables.sqlite3?mode=ro',uri=True)
doc='VIB_financial_statements_2018_consolidated'
for row in c.execute("select table_id,row_idx,cells_json,folded_text from rows where doc_id=? and folded_text like '%du phong rui ro%' order by table_id,row_idx",(doc,)):
 print(*row)
