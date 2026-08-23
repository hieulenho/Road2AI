import json
from pathlib import Path
r={'id':580,'answer':48600.404426,'relevant_tables':['HBC_financial_statements_2016_consolidated|1577','HBC_financial_statements_2015_consolidated|1417'],'variable':'df1','pandas_query':"float(abs(df1.loc[df1['source_id']=='s1','value'].iloc[0]-df1.loc[df1['source_id']=='s2','value'].iloc[0]))",'csv_rows':[
{'ticker':'HBC','year':2016,'value':-48277.443972,'doc_id':'HBC_financial_statements_2016_consolidated','table_id':82,'row_idx':4,'col_idx':3,'raw_value':'(48.277.443.972)','label':'Chi phí thuế thu nhập hoãn lại','source_scale':1.0,'source_id':'s1','computed_answer':48600.404426},
{'ticker':'HBC','year':2015,'value':322.960454,'doc_id':'HBC_financial_statements_2015_consolidated','table_id':66,'row_idx':3,'col_idx':1,'raw_value':'322.960.454','label':'Chi phí (thu nhập) thuế hoãn lại','source_scale':1.0,'source_id':'s2','computed_answer':''}]}
Path('runs/live_search/q580_signed_statement_candidate.json').write_text(json.dumps([r],ensure_ascii=False,indent=2),encoding='utf-8')
