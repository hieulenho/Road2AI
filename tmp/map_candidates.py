import json
from pathlib import Path
from tools.remap_table_refs_to_lines import build_position_map
m,_=build_position_map(Path('artifacts/tables.sqlite3'),Path('.').resolve(),'one-based')
for doc,tid in [('NVB_financial_statements_2016_separate',19),('HBC_financial_statements_2016_consolidated',79),('HBC_financial_statements_2015_consolidated',66),('PLX_financial_statements_2024_consolidated',8),('PLX_financial_statements_2024_consolidated',62),('MSN_financial_statements_2018_consolidated',40)]:
 print(doc,tid,m[(doc,tid)])
