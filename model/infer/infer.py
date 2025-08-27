from pathlib import Path
from paddleocr import PaddleOCR

# Create a single OCR engine once (faster for repeated runs)
_OCR = PaddleOCR(lang="en", use_textline_orientation=True)

def ocr_one_text(image_path: str, min_score: float = 0.50) -> str:
    """Run OCR on one image and return a newline-joined string."""
    img = Path(image_path)
    if not img.exists():
        raise FileNotFoundError(img)

    res = _OCR.predict(str(img))
    if not res:
        return ""

    # Newer PaddleOCR returns list[dict]; older returns list[list]
    try:
        texts, scores = res[0]["rec_texts"], res[0]["rec_scores"]
    except (TypeError, KeyError):
        blocks = res[0]
        texts  = [b[1][0] for b in blocks]
        scores = [b[1][1] for b in blocks]

    keep = [t for t, s in zip(texts, scores) if s >= min_score]
    return "\n".join(keep)

if __name__ == "__main__":
    # Quick local test: change the path to your file
    IMG = r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\model\Dataset\dev\images\Test1n_1.jpg"
    print(ocr_one_text(IMG))
