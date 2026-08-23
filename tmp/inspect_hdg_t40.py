import sqlite3,json
c=sqlite3.connect('file:artifacts/tables.sqlite3?mode=ro',uri=True)
for tid in [40]:
 print('TABLE',tid,c.execute('select context,rows_json from tables where doc_id=? and table_id=?',('HDG_financial_statements_2023_separate',tid)).fetchone()[0])
 for row in c.execute('select row_idx,cells_json from rows where doc_id=? and table_id=? order by row_idx',('HDG_financial_statements_2023_separate',tid)):
  print(row[0],row[1])
