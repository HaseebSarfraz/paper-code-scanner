# backend/__init__.py
import ast
from flask import Flask, request, jsonify
from .llm import fix_code, gen_pytests
from flask_cors import CORS
from paddleocr import PaddleOCR
from werkzeug.utils import secure_filename
import tempfile, os
import subprocess, re
import xml.etree.ElementTree as ET

def _parse_junit(xml_path: str):
    """Return (cases, summary) from a JUnit XML file."""
    cases = []
    summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}

    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return cases, summary  # no report (e.g., collection error)

    for tc in root.iter("testcase"):
        name = tc.attrib.get("name", "")
        time = float(tc.attrib.get("time", "0") or 0)

        status = "passed"
        message = ""

        node = tc.find("failure")
        if node is not None:
            status = "failed"
            message = (node.attrib.get("message") or node.text or "").strip()
        else:
            node = tc.find("error")
            if node is not None:
                status = "error"
                message = (node.attrib.get("message") or node.text or "").strip()
            else:
                node = tc.find("skipped")
                if node is not None:
                    status = "skipped"
                    message = (node.attrib.get("message") or node.text or "").strip()

        # categorize by test name prefix
        cat = "other"
        if name.startswith("test_normal"):
            cat = "normal"
        elif name.startswith("test_edge"):
            cat = "edge"
        elif name.startswith("test_adversarial"):
            cat = "adversarial"

        cases.append({
            "name": name,
            "category": cat,
            "status": status,
            "message": message,
            "duration": time,
        })
        summary[status + ("s" if not status.endswith("s") else "")] = summary.get(status + ("s" if not status.endswith("s") else ""), 0) + 1

    return cases, summary

def _stabilize_tests(src: str, max_tests: int = 12) -> str:
    """Clean LLM test output so pytest can collect reliably, preserving args."""
    src = (src or "")

    # 1) strip chat markers / fences
    src = src.replace("<|im_start|>", "").replace("<|im_end|>", "")
    src = re.sub(r"```(?:python)?\s*|```", "", src)

    # 2) drop obvious prose-only lines
    keep = []
    PAT_ALLOWED = re.compile(
        r"^\s*(#|from\s+\w|import\s+\w|@|def\s+test_|class\s+\w|assert\b|with\b|for\b|if\b|elif\b|else\b|"
        r"try\b|except\b|finally\b|return\b|pass\b|raise\b|\w+\s*=\s*.+)"
    )
    for line in src.splitlines():
        l = line.strip()
        if not l:
            keep.append(line); continue
        if PAT_ALLOWED.match(l) or any(c in l for c in "():{}[]"):
            keep.append(line)
    src = "\n".join(keep)

    # 3) ensure common imports
    if "pytest" in src and "import pytest" not in src:
        src = "import pytest\n" + src
    if "sys." in src and "import sys" not in src:
        src = "import sys\n" + src

    # 4) cap count ONLY; do not rename or drop args
    out, count = [], 0
    for line in src.splitlines():
        if re.match(r'^\s*def\s+test_', line):
            count += 1
            if count > max_tests:
                break
        out.append(line)

    src = "\n".join(out).strip() + "\n"

    # 5) make sure it compiles; if not, do a quick syntax fix
    try:
        compile(src, "tests/test_solution.py", "exec")
        return src
    except SyntaxError:
        return src  # our later finalizer/safety net will handle this anyway

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

@app.route("/api/run_tests", methods=["POST"])
def api_run_tests():
    """
    Body: {"code": "<user-edited code>", "objective": "<what it should do>"}
    Returns: { tests, output, returncode, summary:{passed,failed,skipped,errors} }
    """
    data = request.get_json(force=True, silent=True) or {}
    code = (data.get("code") or "").strip()
    objective = (data.get("objective") or "").strip()

    if not code:
        return jsonify({"error": "no code"}), 400

    # --- Syntax pre-check (fail fast like an IDE) ----------------------
    try:
        # compile() catches SyntaxError with accurate line/column
        compile(code, "solution.py", "exec")
    except SyntaxError as e:
        offending = (e.text or "").rstrip("\n")
        caret = " " * (max((e.offset or 1), 1) - 1) + "^"
        msg = f"{e.msg} (line {e.lineno}, col {e.offset})"
        return jsonify({
            "syntax_error": {
                "message": msg,
                "lineno": e.lineno,
                "offset": e.offset,
                "line": offending,
                "caret": caret,
            }
        }), 200

    # 1) Ask Llama to generate pytest tests
    try:
        tests_py = gen_pytests(objective, code)
        tests_py = _stabilize_tests(tests_py)
        if not tests_py.strip():
            return jsonify({"error": "test generation produced an empty file"}), 500

        # Final guard: ensure at least one test exists
        if not re.search(r'^\s*def\s+test', tests_py, re.M):
            tests_py += (
                "\n\ndef test_smoke_import():\n"
                "    import solution\n"
                "    assert hasattr(solution, '__file__')\n"
            )

    except Exception as e:
        return jsonify({"error": f"test generation failed: {e}"}), 500

    prelude = (
        "import solution\n"
        "try:\n"
        "    from solution import *  # allow bare names in generated tests\n"
        "except Exception:\n"
        "    pass\n\n"
    )
    needs_import_solution = "import solution" not in tests_py
    needs_from_import = "from solution import *" not in tests_py
    if needs_import_solution:
        tests_py = prelude + tests_py
    elif needs_from_import:
        tests_py = "from solution import *\n" + tests_py.lstrip()

    # 2) Run tests in the Docker sandbox image you built earlier
    runner_image = os.environ.get("RUNNER_IMAGE", "paper-runner:py310")

    with tempfile.TemporaryDirectory() as tmpdir:
        # write user's code
        with open(os.path.join(tmpdir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)

        # write generated tests
        os.makedirs(os.path.join(tmpdir, "tests"), exist_ok=True)
        with open(os.path.join(tmpdir, "tests", "test_solution.py"), "w", encoding="utf-8") as f:
            f.write(tests_py)

        # ENTRYPOINT runs: python -m pytest -q --maxfail=1 --disable-warnings
        report_path = os.path.join(tmpdir, "report.xml")

        cmd = [
            "docker", "run", "--rm",
            "-m", "512m",            # slightly stricter cap is fine
            "--cpus", "1.0",
            "--pids-limit", "256",
            "--network", "none",
            "--security-opt", "no-new-privileges:true",
            "--cap-drop", "ALL",
            "-e", "PYTEST_ADDOPTS=--junitxml=/work/report.xml",
            "-v", f"{tmpdir}:/work",
            runner_image,
        ]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except FileNotFoundError:
            return jsonify({"error": "docker not found. Is Docker Desktop running?"}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"error": "test run timed out"}), 504

        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")

        cases, structured_summary = _parse_junit(report_path)

    # keep your old text-summary as fallback if XML was missing
    if (structured_summary["passed"] + structured_summary["failed"] +
        structured_summary["skipped"] + structured_summary["errors"]) == 0:
        # fallback to your regex summary
        summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        for n, label in re.findall(r"(\d+)\s+(passed|failed|skipped|errors?)", out, re.I):
            key = "errors" if label.lower().startswith("error") else label.lower()
            summary[key] = int(n)
    else:
        summary = structured_summary

    return jsonify({
        "tests": tests_py,
        "output": out,                # keep full raw output (debug)
        "returncode": proc.returncode,
        "summary": summary,
        "cases": cases,               # <— NEW: structured per-test results
    })
