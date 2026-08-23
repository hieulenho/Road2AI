import json,zipfile
ids=[682,781,605,837,989,953,594,919,636,626,798,642,872,743,927,996]
with zipfile.ZipFile('submission_vn53.zip') as z:
 d={r['id']:r for r in json.loads(z.read('submission.json'))}
 for qid in ids:
  r=d[qid]; print('\nQ',qid,r['question'],'=>',r['answer']); print(z.read(r['evidence'][0]['csv_path']).decode('utf-8-sig')[:4500])
