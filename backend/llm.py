# backend/llm.py
import re
import requests, textwrap

LLAMA_CHAT_URL = "http://localhost:8080/v1/chat/completions"   # chat endpoint
LLAMA_COMP_URL = "http://localhost:8080/completion"            # fallback

SYSTEM = (
    "You are a strict Python syntax fixer. "
    "Fix ONLY syntax/formatting (indentation, colons, brackets/quotes) and expand "
    "truncated keywords ('f'->'for', 'i'->'if'). Do NOT change identifiers or logic. "
    "Return PLAIN Python only (no markdown/backticks/explanations)."
)

USER_TMPL = "Fix this OCR'd Python. Output only the corrected code.\n\n{code}\n"


def _scrub(s: str) -> str:
    # stop if the model leaked chat tokens, fences, or headings
    for cutter in ("<|im_end|>", "<|im_start|>", "### OCR", "### Fixed"):
        if cutter in s:
            s = s.split(cutter, 1)[0]
    s = s.replace("```python", "").replace("```", "")
    return s.strip()


def fix_code(bad: str, n_predict: int = 256) -> str:
    # --- preferred: chat completions with proper roles/template ---
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": USER_TMPL.format(code=bad)},
        ],
        "temperature": 0.1,
        "n_predict": n_predict,
        # do NOT use "###" stops; they can fire spuriously
        "stop": ["<|im_end|>", "</s>", "<|eot_id|>"],
    }
    try:
        r = requests.post(LLAMA_CHAT_URL, json=payload, timeout=300)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        fixed = _scrub(content)
        if fixed:
            return fixed
    except Exception:
        # fall back to plain completion if chat endpoint not available
        pass

    # --- fallback: instruct-style prompt for /completion ---
    inst = (
        f"<s>[INST]{SYSTEM}\n\n{USER_TMPL.format(code=bad)}[/INST]\n"
    )
    payload2 = {
        "prompt": inst,
        "temperature": 0.1,
        "n_predict": n_predict,
        "stop": [],    # no '###' or backtick stops
    }
    r2 = requests.post(LLAMA_COMP_URL, json=payload2, timeout=300)
    r2.raise_for_status()
    raw = r2.json().get("content") or r2.json()["choices"][0]["text"]
    return _scrub(raw)


def _strip_md(s: str) -> str:
    """Unwrap ``` blocks if present."""
    m = re.search(r"```(?:python)?\s*(.*?)```", s, re.S | re.I)
    return (m.group(1) if m else s).strip()

def _clean_test_source(s: str) -> str:
    """
    Remove common wrappers the model sometimes adds:
    - [PYTEST] / [/PYTEST] / [TESTS] / [CODE]
    - Markdown headings or separators
    - Any lingering code fences (already handled by _strip_md)
    """
    s = _strip_md(s)
    # kill bracket tags on their own lines
    s = re.sub(r'^\s*\[/?(?:PYTEST|TESTS?|CODE)\]\s*$', '', s, flags=re.I | re.M)
    # drop markdown-ish headings/separators the model might emit
    s = re.sub(r'^\s*#{1,6}.*$', '', s, flags=re.M)
    s = re.sub(r'^\s*(?:[-=_]{3,})\s*$', '', s, flags=re.M)
    return s.strip()

TEST_SYSTEM = (
    "You are a senior Python TDD engineer. Return a single valid **Python file** "
    "containing only pytest tests. Import the user's code with `import solution` or "
    "`from solution import *`. Cover normal, edge, and adversarial cases. "
    "Use plain `assert` only. Absolutely NO markdown, NO backticks, NO bracket tags "
    "like [PYTEST]/[TESTS]/[CODE], NO prose, and nothing outside of Python syntax."
)

TEST_USER_TMPL = """\
### Objective
{objective}

### User code
{code}

### Tests
"""

def gen_pytests(objective: str, code: str, max_tokens: int = 800) -> str:
    """Ask Llama for a pytest file that tests `code` against `objective`."""
    chat_payload = {
        "messages": [
            {"role": "system", "content": TEST_SYSTEM},
            {"role": "user", "content": TEST_USER_TMPL.format(objective=objective, code=code)},
        ],
        "temperature": 0.2,
        "n_predict": max_tokens,
        "stop": ["<|im_end|>", "</s>", "<|eot_id|>"],
    }
    try:
        r = requests.post(LLAMA_CHAT_URL, json=chat_payload, timeout=120)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return _clean_test_source(content)
    except Exception:
        inst = f"<s>[INST]{TEST_SYSTEM}\n\n{TEST_USER_TMPL.format(objective=objective, code=code)}[/INST]\n"
        comp_payload = {
            "prompt": inst,
            "temperature": 0.2,
            "n_predict": max_tokens,
            "stop": [],
        }
        r2 = requests.post(LLAMA_COMP_URL, json=comp_payload, timeout=120)
        r2.raise_for_status()
        raw = r2.json().get("content") or r2.json()["choices"][0]["text"]
        return _clean_test_source(raw)

__all__ = ["fix_code", "gen_pytests"]
