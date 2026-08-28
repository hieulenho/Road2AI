import csv
import io
import json
import zipfile


with zipfile.ZipFile("submission_vn53.zip") as archive:
    json_name = next(name for name in archive.namelist() if name.endswith(".json"))
    rows = {int(row["id"]): row for row in json.loads(archive.read(json_name))}
    for qid in (442, 473, 490, 568, 582, 611, 616, 635, 641, 701):
        row = rows[qid]
        print(f"\nQ{qid} answer={row['answer']}")
        path = row["evidence"][0]["csv_path"]
        values = list(csv.DictReader(io.StringIO(archive.read(path).decode("utf-8"))))
        if qid == 442:
            by = {}
            for value in values:
                by.setdefault(value["ticker"], {}).setdefault(int(value["year"]), {})[
                    value["raw_column"]
                ] = float(value["value"])
            ratios = sorted((data[2024]["liabilities"] / data[2024]["equity"], ticker) for ticker, data in by.items())
            median = ratios[len(ratios) // 2][0]
            eligible = []
            for ticker, data in by.items():
                leverage = data[2024]["liabilities"] / data[2024]["equity"]
                growth = data[2025]["net_revenue"] / data[2024]["net_revenue"] - 1
                margin = data[2025]["gross_profit"] / data[2025]["net_revenue"] * 100
                print(ticker, "D/E", leverage, "growth", growth, "margin", margin)
                if leverage < median:
                    eligible.append((growth, ticker, margin))
            print("median", median, "winner", max(eligible))
        else:
            for value in values:
                print({k: v for k, v in value.items() if v not in ("", None)})
