import requests, textwrap

LLAMA_URL = "http://localhost:8080/completions"

PROMPT = textwrap.dedent("""\
### Instruction
You are a Python linter. Fix indentation, add missing colons/brackets,
expand truncated keywords (e.g. “f”→“for”), but **do not** change logic
or rename identifiers. Output only the fixed code.
### Snippet
{code}
### Fixed
""")

LLAMA_URL = "http://localhost:8080/completion"     # singluar

def fix_code(bad: str) -> str:
    payload = {
        "prompt": PROMPT.format(code=bad),
        "n_predict": 128,          #  ≤128 tokens is plenty for one function
        "temperature": 0.1,
        "stream": False,
    }
    r = requests.post(LLAMA_URL, json=payload, timeout=300)  # 5-min cold allowance
    r.raise_for_status()
    raw = r.json()["content"]
    if "### Fixed" in raw:
        raw = raw.split("### Fixed")[-1]
    return raw.strip()

