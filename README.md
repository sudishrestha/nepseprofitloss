# Nepse API CSV Viewer

This is a simple FastAPI web application that allows users to upload a CSV file (like `import_sample.csv`) and displays its contents in a web view (HTML table).

## Features

- Upload a CSV file via a web form
- Display the CSV contents in a styled HTML table

## How to Run

1. Install dependencies (already handled if you followed setup):
   ```
   pip install fastapi uvicorn[standard] jinja2 python-multipart
   ```
2. Start the server:
   ```
   uvicorn main:app --reload
   ```
3. Open your browser and go to [http://localhost:8000](http://localhost:8000)

## File Structure

- `main.py`: FastAPI app entry point
- `templates/`: Jinja2 HTML templates
- `static/`: (optional) for CSS or JS files

## Notes

- The app expects a CSV with headers similar to `import_sample.csv`.
- No data is stored on the server; the CSV is parsed in-memory per upload.
