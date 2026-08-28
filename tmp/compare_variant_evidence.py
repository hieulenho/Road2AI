import csv
import io
import json
import zipfile


ids = [111, 166, 194, 221, 411, 442, 616, 635, 641, 701]


def load(path):
    archive = zipfile.ZipFile(path)
    json_name = next(name for name in archive.namelist() if name.endswith(".json"))
    rows = {int(row["id"]): row for row in json.loads(archive.read(json_name))}
    return archive, rows


base_archive, base = load("submission_vn53.zip")
alt_archive, alt = load("submission_vn.zip")
for qid in ids:
    print(f"\n===== Q{qid} =====")
    for tag, archive, records in (("BASE", base_archive, base), ("ALT", alt_archive, alt)):
        row = records[qid]
        print(tag, "answer=", row["answer"])
        print("tables=", row["relevant_tables"])
        for evidence in row["evidence"]:
            path = evidence["csv_path"]
            values = list(csv.DictReader(io.StringIO(archive.read(path).decode("utf-8"))))
            print(path)
            for value in values:
                compact = {k: v for k, v in value.items() if v not in ("", None)}
                print(compact)
