import glob,json,zipfile,os
for qid,target in [(183,25352217.0),(580,48600.404426),(658,16.70294229036583),(89,726873.0),(19,325.48),(220,1756444759.0)]:
 print('\nQ',qid,'target',target)
 for fn in glob.glob('submission*.zip'):
  try:
   with zipfile.ZipFile(fn) as z:
    d={r['id']:r for r in json.loads(z.read('submission.json'))}
    if abs(float(d[qid]['answer'])-target)<=1e-10*max(1,abs(target)):
     print(os.path.basename(fn))
  except: pass
