from pathlib import Path
from tools.remap_table_refs_to_lines import build_position_map
m,_=build_position_map(Path('artifacts/tables.sqlite3'),Path('.').resolve(),'one-based')
for d,t in [('HBC_financial_statements_2016_consolidated',82),('HBC_financial_statements_2015_consolidated',66)]: print(d,m[(d,t)])
