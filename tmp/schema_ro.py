import sqlite3
p='file:artifacts/tables.sqlite3?mode=ro'
c=sqlite3.connect(p, uri=True)
for row in c.execute("select name,sql from sqlite_master where type='table'"):
 print(row[0],row[1][:500])
