import json,zipfile
for fn,qid in [('submission_vn2.zip',19),('submission_vn2.zip',220),('submission_vn53.zip',19),('submission_vn53.zip',220)]:
 with zipfile.ZipFile(fn) as z:
  rows={r['id']:r for r in json.loads(z.read('submission.json'))}
  r=rows[qid]
  print('\n',fn,qid, r['answer'])
  for e in r['evidence']:
   print(e, z.read(e['csv_path']).decode('utf-8-sig'))
