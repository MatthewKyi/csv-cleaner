from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    file = request.files["file"]

    df = pd.read_csv(file, skip_blank_lines=False)

    df = df.drop_duplicates()
    df = df.dropna(how="all")

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
    app.run(port=5001)