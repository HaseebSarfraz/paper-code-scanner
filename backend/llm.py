# backend/llm.py  (GPU-safe, deterministic, no empty outputs)

import os, re, requests
STOP_CL = ["</s>", "<|im_end|>"]
TIMEOUT_S = int(os.getenv("LLAMA_HTTP_TIMEOUT", "300"))

BASE = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:8080")
SEED = int(os.getenv("LLAMA_SEED", "12345"))
TEMP = float(os.getenv("LLAMA_TEMPERATURE", "0.1"))
TOP_P = float(os.getenv("LLAMA_TOP_P", "0.9"))
TOP_K = int(os.getenv("LLAMA_TOP_K", "40"))

BASE = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:8080")
LLAMA_CHAT_URL = f"{BASE}/v1/chat/completions"
LLAMA_COMP_URL = f"{BASE}/completion"

# deterministic, tweak via .env if you want
GEN = {
    "temperature": float(os.getenv("LLAMA_TEMPERATURE", "0.1")),
    "top_p": float(os.getenv("LLAMA_TOP_P", "0.9")),
    "top_k": int(os.getenv("LLAMA_TOP_K", "40")),
    "n_predict": int(os.getenv("LLAMA_N_PREDICT", "450")),
    "mirostat": 0,
    "seed": int(os.getenv("LLAMA_SEED", "12345")),
}

def _opts(extra=None):
    x = GEN.copy()
    if extra: x.update(extra)
    return x

SYSTEM = (
    "You are a strict Python SYNTAX fixer. "
    "Only fix syntax/formatting (indentation, colons, brackets/quotes) and expand truncated keywords. "
    "Do NOT change identifiers or logic. "
    "Return plain Python only (no markdown/backticks/prose)."
)
USER_TMPL = "Fix this OCR'd Python. Output only the corrected code.\n\n{code}\n"

def _scrub(s: str) -> str:
    # ⚠️ don't split() – it can erase the whole thing if tokens appear at start
    junk = ("<|im_end|>", "<|im_start|>", "<|eot_id|>", "<s>", "</s>")
    for j in junk:
        s = s.replace(j, "")
    s = s.replace("```python", "").replace("```", "")
    return s.strip()


def fix_code(bad: str, n_predict: int = 300) -> str:
    """Deterministic syntax-only repair via /completion first, fallback to /v1/chat/completions."""
    inst = (
        f"<s>[INST] <<SYS>>{SYSTEM}<</SYS>>\n"
        f"{USER_TMPL.format(code=bad)}[/INST]\n"
    )

    # 1) Use /completion with a *prompt*
    comp_payload = {
        "prompt": inst,
        "stop": [],  # avoid accidental early stops
        **_opts({"n_predict": n_predict}),
    }
    r = requests.post(LLAMA_COMP_URL, json=comp_payload, timeout=TIMEOUT_S)
    r.raise_for_status()

    # handle both response shapes
    resp = r.json()
    raw = resp.get("content") or (resp.get("choices") or [{}])[0].get("text", "")
    out = _scrub(raw)
    if out:
        return out

    # 2) Fallback to chat only if needed
    chat_payload = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(code=bad)},
        ],
        **_opts({"n_predict": n_predict}),
        "stop": ["<|im_end|>", "</s>", "<|eot_id|>"],
    }
    r2 = requests.post(LLAMA_CHAT_URL, json=chat_payload, timeout=TIMEOUT_S)
    r2.raise_for_status()
    content = r2.json()["choices"][0]["message"]["content"]
    return _scrub(content)

# ─────────────────────────────────────────────────────────────────────────────

def _strip_md(s: str) -> str:
    m = re.search(r"```(?:python)?\s*(.*?)```", s, re.S | re.I)
    return (m.group(1) if m else s).strip()

def _clean_test_source(s: str) -> str:
    s = _strip_md(s)
    s = re.sub(r'^\s*\[/?(?:PYTEST|TESTS?|CODE|PYTHON)\]\s*$', '', s, flags=re.I|re.M)
    s = re.sub(r'^\s*#{1,6}.*$', '', s, flags=re.M)
    s = re.sub(r'^\s*(?:[-=_]{3,})\s*$', '', s, flags=re.M)
    return s.strip()

def _bind_parametrize_args(src: str) -> str:
    """
    Robust, line-based binder:
    If we see @pytest.mark.parametrize("a, b", ...), remember ("a, b").
    When the next def test_...() has empty args, rewrite to def test_...(a, b).
    Works across blank lines and stacked decorators.
    """
    lines = (src or "").splitlines()
    out = []
    last_params: str | None = None

    # decorator and def detectors
    param_line = re.compile(r'^\s*@pytest\.mark\.parametrize\(\s*([\'"])(?P<params>[^\'"]+)\1\s*,', re.I)
    def_empty = re.compile(r'^(\s*)def\s+(test[A-Za-z0-9_]+)\s*\(\s*\)\s*:\s*$')

    for i, line in enumerate(lines):
        m = param_line.match(line)
        if m:
            last_params = m.group('params').strip()
            out.append(line)
            continue

        dm = def_empty.match(line)
        if dm and last_params:
            indent, name = dm.group(1), dm.group(2)
            out.append(f"{indent}def {name}({last_params}):")
            last_params = None
            continue

        # If we encounter a non-decorator, non-empty line that isn't a def,
        # keep last_params for stacked decorators / blank lines, otherwise leave it.
        out.append(line)

    return "\n".join(out)


def _finalize_pytest_source(src: str) -> str:
    """
    Make the generated pytest file safe to import & collect:
    1) bind @parametrize args into empty test def headers
    2) ensure pytest import and at least one test_ function (append smoke if none)
    3) if it doesn't compile, trim tail until it does
    4) last resort: small syntax-fix; if still bad, return a smoke test
    """
    out = _bind_parametrize_args(src or "").strip()

    # Ensure pytest import
    if out and "import pytest" not in out:
        out = "import pytest\n" + out

    # Ensure at least one test function
    if not re.search(r'^\s*def\s+test', out, re.M):
        out += (
            "\n\ndef test_smoke_import():\n"
            "    import solution\n"
            "    assert hasattr(solution, '__file__')\n"
        )

    # Fast path
    try:
        compile(out, "tests/test_solution.py", "exec")
        return out if out.endswith("\n") else out + "\n"
    except SyntaxError:
        pass

    # Trim trailing lines until it compiles (handles truncated parametrize blocks)
    lines = out.splitlines()
    for _ in range(24):
        if not lines:
            break
        candidate = "\n".join(lines).rstrip() + "\n"
        try:
            compile(candidate, "tests/test_solution.py", "exec")
            return candidate
        except SyntaxError:
            while lines and not lines[-1].strip():
                lines.pop()
            if lines:
                lines.pop()

    # Last resort: tiny syntax-fix
    try:
        fixed = fix_code(out, n_predict=120)
        compile(fixed, "tests/test_solution.py", "exec")
        return fixed if fixed.endswith("\n") else fixed + "\n"
    except Exception:
        return (
            "import pytest\n"
            "def test_smoke_import():\n"
            "    import solution\n"
            "    assert hasattr(solution, '__file__')\n"
        )

TEST_SYSTEM = (
    "You are a meticulous Python testing engineer. "
    "Produce ONE valid Python FILE containing only pytest tests for solution.py — no prose, no comments, no markdown. "
    "Rules:\n"
    "• Import with `import solution` (optionally `from solution import *`).\n"
    "• Use pytest.mark.parametrize heavily; keep the file concise (≤ 120 lines).\n"
    "• Name tests with prefixes: test_normal_, test_edge_, test_adversarial_.\n"
    "• No I/O, no sleeps, no randomness, only plain asserts.\n"
    "Coverage targets (must appear across tests):\n"
    "  – Integers: 0, ±1, large magnitudes (e.g., ±10**6).\n"
    "  – Flat lists: mix positives, negatives, zeros.\n"
    "  – Nested lists: depths 1–5, including nested empty lists.\n"
    "  – Immutability: original input structure must remain unchanged (use deepcopy).\n"
    "  – Adversarial: very deep nest (≈6–8), and a wide list (~1000 items) but keep construction compact.\n"
    "Constraints:\n"
    "  – Do NOT generate extremely long literals or parametrize tables; cap to ≤ 12 tests and ≤ 12 cases per parametrize.\n"
    "  – Do NOT assert exceptions unless they are obvious from the objective.\n"
)

TEST_USER_TMPL = (
    "### Objective\n{objective}\n\n"
    "### User code\n{code}\n\n"
    "### Tests\n"
    "Write only pytest tests that maximize behavioral coverage. Prefer parametrize. "
    "Name tests with prefixes test_normal_, test_edge_, test_adversarial_."
)

def gen_pytests(objective: str, code: str,
                max_tokens: int = int(os.getenv("LLAMA_TEST_N_PREDICT", "280"))) -> str:
    """
    Generate ONE valid pytest file for solution.py using CodeLlama via /completion.
    Uses [INST] format + explicit stop tokens to prevent rambling/timeouts.
    """
    inst = (
        f"<s>[INST] <<SYS>>{TEST_SYSTEM}<</SYS>>\n"
        f"{TEST_USER_TMPL.format(objective=objective, code=code)}[/INST]\n"
    )

    # 1) completion first (preferred)
    payload = {
        "prompt": inst,
        **_opts({"n_predict": max_tokens}),
        "stop": STOP_CL,  # <-- CRITICAL for CodeLlama/Llama-2
    }
    r = requests.post(LLAMA_COMP_URL, json=payload, timeout=TIMEOUT_S)
    r.raise_for_status()

    j = r.json()
    raw = j.get("content") or (j.get("choices") or [{}])[0].get("text", "")
    cleaned = _clean_test_source(_scrub(raw))
    return _finalize_pytest_source(cleaned)

__all__ = ["fix_code", "gen_pytests"]
