from pathlib import Path
from tools.remap_table_refs_to_lines import build_position_map
m,_=build_position_map(Path('artifacts/tables.sqlite3'),Path('.').resolve(),'one-based')
print(m[('VIB_financial_statements_2018_consolidated',3)])
