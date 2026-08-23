import glob,json,zipfile,os
candidates=[(197,-877765.0),(425,0.4494545454545457),(682,1899.321381),(907,2020.0),(989,2024.0)]
for qid,target in candidates:
 print('\n',qid,target)
 for fn in glob.glob('submission*.zip'):
  try:
   with zipfile.ZipFile(fn) as z:
    d={r['id']:r for r in json.loads(z.read('submission.json'))}
    if abs(float(d[qid]['answer'])-target)<=1e-9*max(1,abs(target)):print(os.path.basename(fn))
  except: pass
