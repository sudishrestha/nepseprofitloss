
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import csv
from io import StringIO
from typing import List, Dict

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def parse_csv(file_content: bytes) -> List[Dict[str, str]]:
    s = StringIO(file_content.decode("utf-8"))
    reader = csv.DictReader(s)
    return list(reader)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "headers": None, "rows": None})

@app.post("/upload", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    # Parse both CSVs
    wacc_data = parse_csv(contents)
    # Try to load import_sample.csv from disk
    import os
    wacc_path = os.path.join("templates", "wacc.csv")
    try:
        with open(wacc_path, "rb") as f:
            wacc_file_data = parse_csv(f.read())
    except Exception:
        wacc_file_data = []

    try:
        with open("import_sample.csv", "rb") as f:
            purchase_data = parse_csv(f.read())
    except Exception:
        purchase_data = []

    # Build scrip to WACC info mapping (case-insensitive, strip whitespace)
    wacc_map = {}
    for row in wacc_file_data:
        scrip = row.get("Scrip Name")
        if scrip:
            wacc_map[scrip.strip().upper()] = row
    # Prepare headers
    headers = list(wacc_data[0].keys()) if wacc_data else []
    headers += ["Purchase Rate", "Purchase Total", "Profit/Loss", "% Profit/Loss"]
    # Prepare rows and totals
    rows = []
    total_purchase = 0.0
    total_ltp = 0.0
    total_profit_loss = 0.0
    total_percent_profit_loss = 0.0
    for row in wacc_data:
        scrip = (row.get("Scrip") or row.get("Scrip Name") or "").strip().upper()
        wacc_row = wacc_map.get(scrip)
        purchase_rate = wacc_row.get("WACC Rate") if wacc_row and "WACC Rate" in wacc_row else ""
        try:
            qty_val = row.get("Current Balance") or row.get("WACC Calculated Quantity") or 0
            qty = float(qty_val) if qty_val not in (None, "") else 0
            rate = float(purchase_rate) if purchase_rate not in (None, "") else 0
            purchase_total = round(qty * rate, 2) if rate else 0.0
        except Exception:
            purchase_total = 0.0
        # LTP value
        ltp_val = row.get("Last Transaction Price (LTP)") or row.get("LTP") or 0
        try:
            ltp = float(ltp_val) if ltp_val not in (None, "") else 0
            ltp_total = round(qty * ltp, 2) if ltp else 0.0
        except Exception:
            ltp = 0.0
            ltp_total = 0.0
        profit_loss = round(ltp_total - purchase_total, 2)
        percent_profit_loss = round((profit_loss / purchase_total * 100), 2) if purchase_total else 0.0
        total_purchase += purchase_total
        total_ltp += ltp_total
        total_profit_loss += profit_loss
        total_percent_profit_loss += percent_profit_loss
        # Keep output columns in the same order as headers
        row_out = [row.get(h, "") for h in headers[:-4]] + [purchase_rate, purchase_total, profit_loss, percent_profit_loss]
        rows.append(row_out)
    total_profit_loss = round(total_profit_loss, 2)
    total_percent_profit_loss = round(total_percent_profit_loss, 2)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "headers": headers,
            "rows": rows,
            "total_purchase": total_purchase,
            "total_profit_loss": total_profit_loss,
            "total_percent_profit_loss": total_percent_profit_loss
        }
    )
