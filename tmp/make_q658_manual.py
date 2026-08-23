import json
from pathlib import Path
row={
'id':658,'answer':16.70294229036583,
'relevant_tables':['PLX_financial_statements_2024_consolidated|216'],
'variable':'df1',
'pandas_query':"float(df1.loc[df1['source_id']=='s1','value'].iloc[0] / df1.loc[df1['source_id']=='s2','value'].iloc[0] * 100.0)",
'csv_rows':[
 {'source_id':'s1','ticker':'PLX','year':2024,'value':528005384335.0,'doc_id':'PLX_financial_statements_2024_consolidated','table_id':8,'row_idx':9,'col_idx':3,'label':'Phần lãi trong các công ty liên doanh, liên kết','raw_value':'528.005.384.335','source_scale':1.0},
 {'source_id':'s2','ticker':'PLX','year':2024,'value':3161151940515.0,'doc_id':'PLX_financial_statements_2024_consolidated','table_id':8,'row_idx':19,'col_idx':3,'label':'Lợi nhuận sau thuế TNDN','raw_value':'3.161.151.940.515','source_scale':1.0}
]}
Path('runs/live_search/q658_same_statement_denominator.json').write_text(json.dumps([row],ensure_ascii=False,indent=2),encoding='utf-8')
