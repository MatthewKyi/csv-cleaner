from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
import os
import csv
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def _get_bool_option(name: str, default: bool) -> bool:
    value = request.args.get(name, None)
    if value is None:
        value = request.form.get(name, None)

    if value is None:
        return default

    return str(value).lower() in {"1", "true", "yes", "on"}


def normalize_header(header: str) -> str:
    header = header.strip().lower()
    header = re.sub(r"[^\w\s]", "", header)
    header = re.sub(r"\s+", "_", header)
    return header


@app.route('/', methods=['GET'])
def ping():
    return "OK", 200

@app.get("/")
def ping():
    return {"status": "OK"}


@app.route("/process", methods=["POST"])
def process():

    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]

    if file.filename == "":
        return {"error": "Empty filename"}, 400

    if not file.filename.lower().endswith(".csv"):
        return {"error": "File must be a CSV"}, 400

    remove_duplicates = _get_bool_option("remove_duplicates", default=True)
    remove_empty_rows = _get_bool_option("remove_empty_rows", default=True)
    drop_rows_with_missing = _get_bool_option("drop_rows_with_missing", default=False)
    strip_whitespace = _get_bool_option("strip_whitespace", default=True)
    normalize_headers = _get_bool_option("normalize_headers", default=False)

    try:
        raw = file.read()
        df = None

        for encoding in ["utf-8", "latin-1"]:
            try:
                sample = raw[:5000].decode(encoding, errors="ignore")
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter

                df = pd.read_csv(
                    BytesIO(raw),
                    delimiter=delimiter,
                    encoding=encoding,
                    skip_blank_lines=False
                )
                break
            except Exception:
                df = None

        if df is None:
            return {"error": "Could not parse CSV"}, 400

    except Exception:
        return {"error": "Invalid CSV format"}, 400

    if len(df) > 500000:
        return {"error": "CSV too large"}, 400

    original_rows = len(df)

    if strip_whitespace:
        df.columns = df.columns.str.strip()
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    if normalize_headers:
        df.columns = [normalize_header(col) for col in df.columns]

    duplicates_removed = 0
    if remove_duplicates:
        duplicates_removed = df.duplicated().sum()
        df = df.drop_duplicates()

    empty_rows_removed = 0
    if remove_empty_rows:
        empty_rows_removed = df.isna().all(axis=1).sum()
        df = df.dropna(how="all")

    rows_with_missing_removed = 0
    if drop_rows_with_missing:
        rows_with_missing_removed = df.isna().any(axis=1).sum()
        df = df.dropna(how="any")

    cleaned_rows = len(df)

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"cleaned_{file.filename}"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))