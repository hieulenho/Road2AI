import json
from pathlib import Path
q=json.loads(Path('runs/agent_easy_resolver_cv/unoverridden_review_queue.json').read_text(encoding='utf-8'))
e=next(x for x in q if x['id']==183)
t=e['top']
row={
 'id':183,
 'answer':float(t['answer_value']),
 'relevant_tables':[f"{t['doc_id']}|1022"],
 'variable':'df',
 'csv_row':{
   'candidate_id':t['candidate_id'],'ticker':'NVB','report_year':2016,'scope':'parent','doc_id':t['doc_id'],'table_id':t['table_id'],'row_idx':t['row_idx'],'col_idx':t['col_idx'],'row_label':t['row_label'],'section':t['section'],'column_header':t['column_header'],'table_context':t['table_context'],'raw_value':t['raw_value'],'raw_number':25352217.0,'source_scale':1000000.0,'requested_scale':1000000.0,'answer_value':float(t['answer_value'])
 }
}
Path('runs/live_search/q183_total_loans_candidate.json').write_text(json.dumps([row],ensure_ascii=False,indent=2),encoding='utf-8')
