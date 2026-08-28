import json
import zipfile


with zipfile.ZipFile("submission_vn53.zip") as archive:
    rows = json.loads(archive.read("submission.json"))

positive_markers = (
    " cao hơn ",
    " lớn hơn ",
    " nhiều hơn ",
    " vượt ",
    " tăng bao nhiêu",
    " tăng so với",
    " tăng từ",
    " tăng %",
    " thấp hơn ",
    " bé hơn ",
    " ít hơn ",
    " giảm bao nhiêu",
)

for row in rows:
    question = str(row["question"]).lower()
    answer = float(row["answer"])
    if answer < 0 and any(marker in question for marker in positive_markers):
        print(f"Q{row['id']} ans={answer}: {row['question']}")
