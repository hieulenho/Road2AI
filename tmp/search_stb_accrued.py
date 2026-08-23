import sqlite3
c=sqlite3.connect('file:artifacts/tables.sqlite3?mode=ro',uri=True)
for doc in ['STB_financial_statements_2017_consolidated','STB_financial_statements_2022_consolidated','STB_financial_statements_2024_consolidated']:
 print('\nDOC',doc)
 for row in c.execute("select table_id,row_idx,cells_json,folded_text from rows where doc_id=? and (folded_text like '%lai du thu%' or folded_text like '%lai tu cho vay khach hang%') order by table_id,row_idx",(doc,)):
  print(*row)
