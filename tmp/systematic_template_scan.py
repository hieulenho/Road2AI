import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "runs/template_review_all_with_audited.json").read_text(encoding="utf-8"))
db = sqlite3.connect(ROOT / "artifacts/tables_v2.sqlite3")
db.row_factory = sqlite3.Row

KNOWN = {
    755, 821, 787, 50, 244, 298, 59, 95, 671, 611, 827, 888,
    300, 49, 358, 676, 659, 208, 352, 169, 997, 855, 248, 66,
}

if len(sys.argv) > 1 and sys.argv[1] == "keywords":
    keywords = (
        "tổng ", "tổng số", "giá trị còn lại", "thuần", "ròng",
        "dự phòng", "chênh lệch", "biến động", "các khoản", "chi phí",
        "tỷ trọng",
    )
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        question = q["question"].lower()
        if not any(k in question for k in keywords):
            continue
        labels = " | ".join(str(src.get("label", "")) for src in q.get("source_rows", []))
        print(f"Q{q['id']} ans={q['answer']} conf={q['confidence']:.3f} {q['question']}")
        print(f"  {labels}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "multi_numeric":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        question = q["question"].lower()
        if not any(k in question for k in ("giá trị còn lại", "thuần", "tổng", "ròng", "các khoản")):
            continue
        for src in q.get("source_rows", []):
            rec = db.execute(
                "SELECT rows_json,header_rows_json,context FROM tables WHERE doc_id=? AND table_id=?",
                (src["doc_id"], int(src["table_id"])),
            ).fetchone()
            if not rec:
                continue
            table_rows = json.loads(rec["rows_json"])
            row_idx = int(src["row_idx"])
            if row_idx >= len(table_rows):
                continue
            cells = table_rows[row_idx]
            nums = []
            for ci, cell in enumerate(cells):
                raw = str(cell).strip()
                if re.fullmatch(r"\(?[-+]?\d[\d., ]*\)?", raw):
                    nums.append((ci, raw))
            if len(nums) < 3:
                continue
            header_ids = json.loads(rec["header_rows_json"])
            headers = [table_rows[i] for i in header_ids if i < len(table_rows)]
            print(f"Q{q['id']} {q['question']}")
            print(f"  doc={src['doc_id']} t{src['table_id']} r{row_idx} selected_c={src['col_idx']} raw={src['raw_value']} label={src['label']}")
            print(f"  headers={headers}")
            print(f"  cells={cells}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "signed":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        signed = [src for src in q.get("source_rows", []) if "(" in str(src.get("raw_value", ""))]
        if not signed:
            continue
        print(f"Q{q['id']} ans={q['answer']} {q['method']} conf={q['confidence']:.3f} {q['question']}")
        for src in signed:
            print(f"  {src['year']} value={src['value']} raw={src['raw_value']} label={src['label']} doc={src['doc_id']} t{src['table_id']} r{src['row_idx']} c{src['col_idx']}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "missed_total":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        for src in q.get("source_rows", []):
            rec = db.execute(
                "SELECT rows_json,header_rows_json,context FROM tables WHERE doc_id=? AND table_id=?",
                (src["doc_id"], int(src["table_id"])),
            ).fetchone()
            if not rec:
                continue
            table_rows = json.loads(rec["rows_json"])
            row_idx, col = int(src["row_idx"]), int(src["col_idx"])
            if row_idx >= len(table_rows):
                continue
            cells = table_rows[row_idx]
            header_ids = json.loads(rec["header_rows_json"])
            headers = [table_rows[i] for i in header_ids if i < len(table_rows)]
            col_headers = [str(h[col]) for h in headers if col < len(h)]
            selected_header = " | ".join(col_headers)
            total_cols = []
            for ci in range(len(cells)):
                hb = " | ".join(str(h[ci]) for h in headers if ci < len(h)).lower()
                if "tổng" in hb or "tong" in hb or "cộng" in hb:
                    total_cols.append((ci, hb, cells[ci]))
            if total_cols and col not in {z[0] for z in total_cols}:
                print(f"Q{q['id']} ans={q['answer']} {q['question']}")
                print(f"  doc={src['doc_id']} t{src['table_id']} r{row_idx} c{col} selected_header={selected_header} raw={src['raw_value']} label={src['label']}")
                print(f"  total_cols={total_cols}")
                print(f"  cells={cells}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "prior_total":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        for src in q.get("source_rows", []):
            rec = db.execute(
                "SELECT rows_json,context FROM tables WHERE doc_id=? AND table_id=?",
                (src["doc_id"], int(src["table_id"])),
            ).fetchone()
            if not rec:
                continue
            trs = json.loads(rec["rows_json"])
            ri, ci = int(src["row_idx"]), int(src["col_idx"])
            if ri >= len(trs) or ri == 0:
                continue
            cells = trs[ri]
            priors = trs[max(0,ri-3):ri]
            total_cols=[]
            for cj in range(len(cells)):
                hb=" | ".join(str(h[cj]) for h in priors if cj < len(h)).lower()
                if ("tổng" in hb or "tong" in hb or "cộng" in hb) and cj != ci:
                    total_cols.append((cj,hb,cells[cj]))
            if not total_cols:
                continue
            print(f"Q{q['id']} ans={q['answer']} {q['question']}")
            print(f"  doc={src['doc_id']} t{src['table_id']} r{ri} c{ci} raw={src['raw_value']} label={src['label']}")
            print(f"  priors={priors}")
            print(f"  total_cols={total_cols}")
            print(f"  cells={cells}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "categorical_columns":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        for src in q.get("source_rows", []):
            rec = db.execute(
                "SELECT rows_json,header_rows_json,context FROM tables WHERE doc_id=? AND table_id=?",
                (src["doc_id"], int(src["table_id"])),
            ).fetchone()
            if not rec:
                continue
            trs=json.loads(rec["rows_json"]); ri=int(src["row_idx"]); ci=int(src["col_idx"])
            if ri >= len(trs): continue
            cells=trs[ri]
            numeric=[]
            for cj,cell in enumerate(cells):
                raw=str(cell).strip()
                if re.fullmatch(r"\(?[-+]?\d[\d., ]*\)?",raw): numeric.append((cj,raw))
            if len(numeric)<2: continue
            hids=set(json.loads(rec["header_rows_json"]))
            hids.update(range(max(0,ri-3),ri))
            hs=[trs[i] for i in sorted(hids) if 0<=i<len(trs)]
            sh=" | ".join(str(h[ci]) for h in hs if ci<len(h)).lower()
            if re.search(r"20\d{2}|19\d{2}|năm nay|năm trước|cuối năm|đầu năm|cuối kỳ|đầu kỳ|31[/.-]12|01[/.-]01",sh):
                continue
            print(f"Q{q['id']} {q['question']}")
            print(f"  doc={src['doc_id']} t{src['table_id']} r{ri} c{ci} raw={src['raw_value']} label={src['label']} selected_header={sh}")
            print(f"  headers={hs}")
            print(f"  cells={cells}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "scope":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        qt=q["question"].lower()
        wants_parent=("công ty mẹ" in qt or "bctc riêng" in qt or "báo cáo tài chính công ty mẹ" in qt or "phạm vi công ty mẹ" in qt)
        wants_cons=("hợp nhất" in qt)
        bad=[]
        for src in q.get("source_rows",[]):
            doc=src["doc_id"].lower()
            if wants_parent and "separate" not in doc: bad.append(src)
            if wants_cons and "consolidated" not in doc: bad.append(src)
        if bad:
            print(f"Q{q['id']} {q['question']}")
            for src in bad: print(f"  {src['doc_id']} t{src['table_id']} r{src['row_idx']} c{src['col_idx']} raw={src['raw_value']} label={src['label']}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "near_total_row":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN or "tổng" not in q["question"].lower():
            continue
        for src in q.get("source_rows",[]):
            if "tổng" in str(src.get("label","")).lower() or "cộng" in str(src.get("label","")).lower():
                continue
            rec=db.execute("SELECT rows_json FROM tables WHERE doc_id=? AND table_id=?",(src["doc_id"],int(src["table_id"]))).fetchone()
            if not rec: continue
            trs=json.loads(rec["rows_json"]); ri=int(src["row_idx"]); ci=int(src["col_idx"])
            nearby=[]
            for rj in range(max(0,ri-8),min(len(trs),ri+9)):
                if rj==ri: continue
                label=str(trs[rj][0] if trs[rj] else "")
                if ("tổng" in label.lower() or "cộng" in label.lower()) and ci<len(trs[rj]):
                    nearby.append((rj,label,trs[rj][ci],trs[rj]))
            if nearby:
                print(f"Q{q['id']} ans={q['answer']} {q['question']}")
                print(f"  source {src['doc_id']} t{src['table_id']} r{ri} c{ci} raw={src['raw_value']} label={src['label']}")
                print(f"  nearby_total={nearby}")
    raise SystemExit

if len(sys.argv) > 1 and sys.argv[1] == "cross_table_ratio":
    for q in rows:
        if q.get("audited_override") or q["id"] in KNOWN:
            continue
        if q.get("method") not in ("template:ratio","template:mean","template:argmax","template:maximum"):
            continue
        groups={}
        for s in q.get("source_rows",[]): groups.setdefault((s["ticker"],s["year"]),[]).append(s)
        if not any(len({s["table_id"] for s in ss})>1 for ss in groups.values()): continue
        if not any(k in q["question"].lower() for k in ("tỷ trọng","tỷ lệ","trên tổng","gấp","thuần","ròng")): continue
        print(f"Q{q['id']} ans={q['answer']} {q['question']}")
        for s in q.get("source_rows",[]): print(f"  {s['ticker']} {s['year']} {s['doc_id']} t{s['table_id']} r{s['row_idx']} c{s['col_idx']} raw={s['raw_value']} label={s['label']}")
    raise SystemExit

for q in rows:
    if q.get("audited_override"):
        continue
    for src in q.get("source_rows", []):
        rec = db.execute(
            "SELECT rows_json,header_rows_json,context FROM tables WHERE doc_id=? AND table_id=?",
            (src["doc_id"], int(src["table_id"])),
        ).fetchone()
        if not rec:
            continue
        table_rows = json.loads(rec["rows_json"])
        header_ids = json.loads(rec["header_rows_json"])
        col = int(src["col_idx"])
        header_bits = []
        for idx in header_ids:
            if idx < len(table_rows) and col < len(table_rows[idx]):
                header_bits.append(str(table_rows[idx][col]))
        header = " | ".join(header_bits)
        section = src.get("section", "")
        combined = f"{header} {section}"
        target_year = str(src["year"])
        years = re.findall(r"20\d{2}|19\d{2}", combined)
        bad_year = bool(years and target_year not in years)
        bad_period = bool(re.search(r"đầu năm|dau nam|đầu kỳ|dau ky|năm trước|nam truoc", combined, re.I))
        if bad_year or bad_period:
            print(
                f"Q{q['id']} {q['method']} target={target_year} selected=c{col} "
                f"header=[{header}] section=[{section}] raw={src['raw_value']} "
                f"label=[{src['label']}] doc={src['doc_id']} t{src['table_id']} r{src['row_idx']}"
            )
            print(f"  {q['question']}")
