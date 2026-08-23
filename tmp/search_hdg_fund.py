import sqlite3,json,unicodedata
c=sqlite3.connect('file:artifacts/tables.sqlite3?mode=ro',uri=True)
for row in c.execute("select table_id,row_idx,cells_json,folded_text from rows where doc_id=? and (folded_text like '%khen thuong%' or folded_text like '%phuc loi%') order by table_id,row_idx",('HDG_financial_statements_2023_separate',)):
 print(row[0],row[1],row[2],row[3])
