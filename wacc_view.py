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
    try:
        with open("import_sample.csv", "rb") as f:
            purchase_data = parse_csv(f.read())
    except Exception:
        purchase_data = []
    # Build scrip to purchase info mapping
    purchase_map = {row["Scrip"].strip(): row for row in purchase_data if "Scrip" in row}
    # Prepare headers
    headers = list(wacc_data[0].keys()) if wacc_data else []
    headers += ["Purchase Rate", "Purchase Total"]
    # Prepare rows
    rows = []
    for row in wacc_data:
        scrip = row.get("Scrip Name") or row.get("Scrip")
        purchase_row = purchase_map.get(scrip.strip() if scrip else "")
        purchase_rate = purchase_row["Last Closing Price"] if purchase_row else ""
        try:
            qty = float(row.get("WACC Calculated Quantity", 0))
            rate = float(purchase_rate) if purchase_rate else 0
            purchase_total = qty * rate if rate else ""
        except Exception:
            purchase_total = ""
        row_out = list(row.values()) + [purchase_rate, purchase_total]
        rows.append(row_out)
    return templates.TemplateResponse("index.html", {"request": request, "headers": headers, "rows": rows})
