# backend/llm.py
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
