import json,zipfile
with zipfile.ZipFile('submission_vn53.zip') as z:
 d={r['id']:r for r in json.loads(z.read('submission.json'))}
 for qid in [856,989,953,901,864,847,879,985]:
  r=d[qid]; print('\nQ',qid,r['question'],'=>',r['answer']); print(z.read(r['evidence'][0]['csv_path']).decode('utf-8-sig')[:7000])
