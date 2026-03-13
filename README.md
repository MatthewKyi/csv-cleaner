CSV Cleaner
---
Upload a messy CSV file to automatically detect and fix common issues. Remove duplicate rows and empty records. Trim whitespace and handle missing values.

Features
---

- Remove duplicate rows  
- Remove completely empty rows  
- Remove rows with any missing values (optional)  
- Trim whitespace from column headers and string cells  
- Preserve column structure  
- Simple file upload API for easy integration

API Usage
---

Send a `POST` request to the `/process` endpoint with a CSV file and optional cleaning flags.

Example with `curl`:

```bash
curl -X POST "http://localhost:5001/process?remove_duplicates=true&remove_empty_rows=true&drop_rows_with_missing=false&strip_whitespace=true" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your.csv" \
  -o cleaned.csv
```

### Endpoint

- `POST /process`

### Request

- **Body**: `multipart/form-data` containing:
  - `file`: CSV file to clean
- **Query or form parameters** (all optional):
  - `remove_duplicates` (default: `true`)
  - `remove_empty_rows` (default: `true`)
  - `drop_rows_with_missing` (default: `false`)
  - `strip_whitespace` (default: `true`)

### Response

- On success: cleaned CSV file returned as a download (`text/csv`).
- On error: JSON error message with an appropriate HTTP status code.