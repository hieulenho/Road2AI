import json,zipfile
for fn in ['submission_vn2.zip','submission_vn3.zip','submission_vn53.zip']:
 with zipfile.ZipFile(fn) as z:
  rows=json.loads(z.read('submission.json'))
  d={r['id']:r for r in rows}
  print('\n',fn)
  for qid in [19,82,120,220,411,442,89,580,658,183]:
   r=d[qid]
   print(qid, r['question'], '=>', r['answer'], r['relevant_tables'], r['pandas_query'])
