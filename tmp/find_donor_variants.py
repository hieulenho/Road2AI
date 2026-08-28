import glob
import json
import zipfile


targets = {
    111: 132.906342891,
    166: 1.348,
    194: -10054.0,
    221: 10.575727611,
    411: 1.0,
    442: 31.1319542403,
    473: 191.13545996,
    490: 191.13545996,
    568: 191.13545996,
    582: -8.06477728192,
    611: 2766768.0,
    616: 1.62321971516,
    635: 19.58084103,
    641: 0.489705383,
    701: 2.2803494469,
}

for path in sorted(glob.glob("submission_vn*.zip")):
    try:
        with zipfile.ZipFile(path) as archive:
            name = next(n for n in archive.namelist() if n.endswith(".json"))
            rows = {int(r["id"]): r for r in json.loads(archive.read(name))}
    except Exception:
        continue
    matches = []
    for qid, value in targets.items():
        if qid in rows and abs(float(rows[qid]["answer"]) - value) <= 1e-9 * max(1.0, abs(value)):
            matches.append(qid)
    if matches:
        print(path, matches)

with zipfile.ZipFile("submission_vn.zip") as archive:
    json_name = next(n for n in archive.namelist() if n.endswith(".json"))
    rows = {int(r["id"]): r for r in json.loads(archive.read(json_name))}
for qid in targets:
    if qid == 611:
        continue
    row = rows[qid]
    print("\n", qid, row["question"])
    print("answer", row["answer"])
    print("tables", row["relevant_tables"])
    print("query", row["pandas_query"])
