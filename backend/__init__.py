# backend/__init__.py
from flask import Flask, request, jsonify
from .llm import fix_code
from flask_cors import CORS
from paddleocr import PaddleOCR
from werkzeug.utils import secure_filename
import tempfile, os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ───── create ONE Paddle instance (starts once, re-used for every call) ──────
# • english charset → no CJK dictionary noise
# • turn OFF textline orientation – in code snippets everything is left-to-right
# • no angle classifier – speeds things up & avoids occasional rotations
ocr = PaddleOCR(
       lang="en",
       use_textline_orientation=True)

@app.route("/api/ocr", methods=["POST"])
def api_ocr():
    """
    Accepts a multipart/form-data field called 'file'
    Returns {"text": "..."} containing the recognised code.
    """
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400

    f = request.files["file"]
    fname = secure_filename(f.filename)

    # write to a temp-file so PaddleOCR can read it
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, fname)
        f.save(path)

        result = ocr.ocr(path)
        if not result:
            return jsonify({"text": ""})

        texts = result[0]["rec_texts"] if isinstance(result[0], dict) else [b[1][0] for b in result[0]]
        scores = result[0].get("rec_scores", [1.0]*len(texts)) if isinstance(result[0], dict) else [b[1][1] for b in result[0]]

        junk_exact  = {"cs"}                              # the little “CS” line
        junk_substrs = ("camscanner",)                     # matches ScannedwithCamScanner / Scanned with CamScanner

        lines = []
        for t, s in zip(texts, scores):
            t = (t or "").strip()
            if not t:
                continue
            tl = t.lower()
            if tl in junk_exact or any(sub in tl for sub in junk_substrs):
                continue
            # only drop *obvious* garbage (tiny + ultra low conf)
            if s < 0.05 and len(t) <= 2:
                continue
            lines.append(t)

        raw = "\n".join(lines)

    fixed = fix_code(raw)

    return jsonify({"text": fixed})
    # return jsonify({"text": fixed, "raw": raw, "scores": [round(float(s), 3) for s in scores]})
    # return jsonify({"text": raw})

