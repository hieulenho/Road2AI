import json
from pathlib import Path
r={'id':197,'answer':-877765.0,'relevant_tables':['VIB_financial_statements_2018_consolidated|178'],'variable':'df','csv_row':{'candidate_id':'q197_statement_total','ticker':'VIB','report_year':2018,'scope':'consolidated','doc_id':'VIB_financial_statements_2018_consolidated','table_id':3,'row_idx':10,'col_idx':2,'row_label':'Dự phòng rủi ro cho vay khách hàng','section':'TÀI SẢN','column_header':'31/12/2018 triệu đồng','raw_value':'(877.765)','raw_number':-877765.0,'source_scale':1000000.0,'requested_scale':1000000.0,'answer_value':-877765.0}}
Path('runs/live_search/q197_signed_statement_total.json').write_text(json.dumps([r],ensure_ascii=False,indent=2),encoding='utf-8')
