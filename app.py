from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def _get_bool_option(name: str, default: bool) -> bool:
    value = request.args.get(name, None)
    if value is None:
        value = request.form.get(name, None)

    if value is None:
        return default

    return str(value).lower() in {"1", "true", "yes", "on"}


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

    try:
        df = pd.read_csv(file, skip_blank_lines=False)
    except Exception:
        return {"error": "Invalid CSV format"}, 400

    original_rows = len(df)

    if strip_whitespace:
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda value: value.strip() if isinstance(value, str) else value)

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

    print(
        f"Rows: {original_rows} | "
        f"Duplicates removed: {duplicates_removed} | "
        f"Empty rows removed: {empty_rows_removed} | "
        f"Rows with missing values removed: {rows_with_missing_removed} | "
        f"Remaining rows: {cleaned_rows}"
    )

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