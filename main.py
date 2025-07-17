
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import csv
from io import StringIO
from typing import List, Dict


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory cache for uploaded files
from threading import Lock
cache = {"wacc": None, "share": None}
cache_lock = Lock()

def parse_csv(file_content: bytes) -> List[Dict[str, str]]:
    s = StringIO(file_content.decode("utf-8"))
    reader = csv.DictReader(s)
    return list(reader)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global cache
    with cache_lock:
        wacc_bytes = cache["wacc"]
        share_bytes = cache["share"]
    if not wacc_bytes or not share_bytes:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "headers": None,
                "rows": None,
                "total_purchase": 0.0,
                "total_profit_loss": 0.0,
                "total_percent_profit_loss": 0.0,
                "no_data": True
            }
        )

    wacc_data = parse_csv(wacc_bytes)
    share_data = parse_csv(share_bytes)

    wacc_map = {}
    for row in wacc_data:
        scrip = row.get("Scrip Name")
        if scrip:
            wacc_map[scrip.strip().upper()] = row

    headers = list(share_data[0].keys()) if share_data else []
    headers += ["Purchase Rate", "Purchase Total", "Profit/Loss", "% Profit/Loss"]
    rows = []
    total_purchase = 0.0
    total_ltp = 0.0
    total_profit_loss = 0.0
    total_percent_profit_loss = 0.0
    for row in share_data:
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
        row_out = [row.get(h, "") for h in headers[:-4]] + [purchase_rate, purchase_total, profit_loss, percent_profit_loss]
        rows.append(row_out)

    total_profit_loss = round(total_profit_loss, 2)
    # Calculate total percent profit/loss as (total profit loss / total purchase) * 100
    total_percent_profit_loss = round((total_profit_loss / total_purchase * 100), 2) if total_purchase else 0.0

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "headers": headers,
            "rows": rows,
            "total_purchase": total_purchase,
            "total_profit_loss": total_profit_loss,
            "total_percent_profit_loss": total_percent_profit_loss,
            "no_data": False
        }
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_csv(
    request: Request,
    wacc_file: UploadFile = File(None),
    share_file: UploadFile = File(None),
):
    # Use uploaded files if provided, else use cache
    global cache
    with cache_lock:
        if wacc_file and wacc_file.filename:
            wacc_bytes = await wacc_file.read()
            cache["wacc"] = wacc_bytes
        if share_file and share_file.filename:
            share_bytes = await share_file.read()
            cache["share"] = share_bytes
        wacc_bytes = cache["wacc"]
        share_bytes = cache["share"]

    if not wacc_bytes or not share_bytes:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "headers": None,
                "rows": None,
                "total_purchase": 0.0,
                "total_profit_loss": 0.0,
                "total_percent_profit_loss": 0.0,
                "no_data": True
            }
        )

    wacc_data = parse_csv(wacc_bytes)
    share_data = parse_csv(share_bytes)

    # Build scrip to WACC info mapping (case-insensitive, strip whitespace)
    wacc_map = {}
    for row in wacc_data:
        scrip = row.get("Scrip Name")
        if scrip:
            wacc_map[scrip.strip().upper()] = row

    headers = list(share_data[0].keys()) if share_data else []
    headers += ["Purchase Rate", "Purchase Total", "Profit/Loss", "% Profit/Loss"]
    rows = []
    total_purchase = 0.0
    total_ltp = 0.0
    total_profit_loss = 0.0
    total_percent_profit_loss = 0.0
    for row in share_data:
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
        row_out = [row.get(h, "") for h in headers[:-4]] + [purchase_rate, purchase_total, profit_loss, percent_profit_loss]
        rows.append(row_out)
    total_profit_loss = round(total_profit_loss, 2)
    # Calculate total percent profit/loss as (total profit loss / total purchase) * 100
    total_percent_profit_loss = round((total_profit_loss / total_purchase * 100), 2) if total_purchase else 0.0

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
