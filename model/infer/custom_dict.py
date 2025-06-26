from pathlib import Path
from paddleocr import PaddleOCR

DICT_PATH = Path(
    r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\model\custom_dict\python_ascii.txt"
)
def custom_dict():

    if DICT_PATH.exists():        # ← prevents re-writing every run
        return

    chars = [chr(i) for i in range(32, 127)]
    DICT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with DICT_PATH.open("w", encoding="utf-8") as f:
        f.write("\n".join(chars))

    print(f"[SETUP] Wrote {len(chars)} characters → {DICT_PATH}")


custom_dict()
