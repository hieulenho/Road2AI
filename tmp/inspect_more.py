import json,zipfile
with zipfile.ZipFile('submission_vn53.zip') as z:
 d={r['id']:r for r in json.loads(z.read('submission.json'))}
 for qid in [425,580,658,797,907,935]:
  r=d[qid]
  print('\nQ',qid,r['question'],'=>',r['answer'])
  print(r['relevant_docs'],r['relevant_tables'],r['pandas_query'])
  for e in r['evidence']:
   print(z.read(e['csv_path']).decode('utf-8-sig')[:5000])
