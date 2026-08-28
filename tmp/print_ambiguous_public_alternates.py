import json
import zipfile


inference = json.load(open("runs/live_search/public_answer_state_inference.json", encoding="utf-8"))
with zipfile.ZipFile("submission_vn53.zip") as archive:
    json_name = next(name for name in archive.namelist() if name.endswith(".json"))
    rows = {int(row["id"]): row for row in json.loads(archive.read(json_name))}

for item in inference:
    if int(item["delta_max"]) != 1:
        continue
    row = rows[int(item["qid"])]
    print(
        f"Q{item['qid']} base={item['base']} alt={item['alt']} :: "
        f"{row['question']}"
    )
