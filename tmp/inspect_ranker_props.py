import json,zipfile
with zipfile.ZipFile('submission_vn53.zip') as z:
 d={r['id']:r for r in json.loads(z.read('submission.json'))}
 for qid in [591,1000,1008,583,586,589,595,596,597]:
  r=d[qid]; print('\nQ',qid,r['question'],'=>',r['answer']); print(r['relevant_tables']); print(z.read(r['evidence'][0]['csv_path']).decode('utf-8-sig')[:7000])
