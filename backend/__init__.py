from flask import Flask, request, jsonify
from .llm import fix_code, gen_pytests
from flask_cors import CORS
from paddleocr import PaddleOCR
from werkzeug.utils import secure_filename
import tempfile, os
import subprocess, re
import xml.etree.ElementTree as ET

def _parse_junit(xml_path: str):

    cases = []
    summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}

    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return cases, summary

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

        # Categorizing test cases
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

    src = (src or "")

    src = src.replace("<|im_start|>", "").replace("<|im_end|>", "")
    src = re.sub(r"```(?:python)?\s*|```", "", src)

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

    if "pytest" in src and "import pytest" not in src:
        src = "import pytest\n" + src
    if "sys." in src and "import sys" not in src:
        src = "import sys\n" + src

    out, count = [], 0
    for line in src.splitlines():
        if re.match(r'^\s*def\s+test_', line):
            count += 1
            if count > max_tests:
                break
        out.append(line)

    src = "\n".join(out).strip() + "\n"

    try:
        compile(src, "tests/test_solution.py", "exec")
        return src
    except SyntaxError:
        return src

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

ocr = PaddleOCR(
       lang="en",
       use_textline_orientation=True)

@app.route("/api/ocr", methods=["POST"])
def api_ocr():

    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400

    f = request.files["file"]
    fname = secure_filename(f.filename)

    # writing to a temp-file so PaddleOCR can read it
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, fname)
        f.save(path)

        result = ocr.ocr(path)
        if not result:
            return jsonify({"text": ""})

        texts = result[0]["rec_texts"] if isinstance(result[0], dict) else [b[1][0] for b in result[0]]
        scores = result[0].get("rec_scores", [1.0]*len(texts)) if isinstance(result[0], dict) else [b[1][1] for b in result[0]]

        junk_exact  = {"cs"}
        junk_substrs = ("camscanner",)   # matches ScannedwithCamScanner / Scanned with CamScanner

        lines = []
        for t, s in zip(texts, scores):
            t = (t or "").strip()
            if not t:
                continue
            tl = t.lower()
            if tl in junk_exact or any(sub in tl for sub in junk_substrs):
                continue
            if s < 0.05 and len(t) <= 2:
                continue
            lines.append(t)

        raw = "\n".join(lines)

    fixed = fix_code(raw)

    return jsonify({"text": fixed})


@app.route("/api/run_tests", methods=["POST"])
def api_run_tests():

    data = request.get_json(force=True, silent=True) or {}
    code = (data.get("code") or "").strip()
    objective = (data.get("objective") or "").strip()

    if not code:
        return jsonify({"error": "no code"}), 400

    try:
        # It catches errors at runtime and also specifies the exact line/col in code
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

    # 2) Run tests in the Docker sandbox
    runner_image = os.environ.get("RUNNER_IMAGE", "paper-runner:py310")

    with tempfile.TemporaryDirectory() as tmpdir:

        with open(os.path.join(tmpdir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)

        # write generated tests
        os.makedirs(os.path.join(tmpdir, "tests"), exist_ok=True)
        with open(os.path.join(tmpdir, "tests", "test_solution.py"), "w", encoding="utf-8") as f:
            f.write(tests_py)

        report_path = os.path.join(tmpdir, "report.xml")

        cmd = [
            "docker", "run", "--rm",
            "-m", "512m",
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

    if (structured_summary["passed"] + structured_summary["failed"] +
        structured_summary["skipped"] + structured_summary["errors"]) == 0:

        summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        for n, label in re.findall(r"(\d+)\s+(passed|failed|skipped|errors?)", out, re.I):
            key = "errors" if label.lower().startswith("error") else label.lower()
            summary[key] = int(n)
    else:
        summary = structured_summary

    return jsonify({
        "tests": tests_py,
        "output": out,
        "returncode": proc.returncode,
        "summary": summary,
        "cases": cases,
    })
