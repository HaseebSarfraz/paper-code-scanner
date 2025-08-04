from pathlib import Path
import json
from paddleocr import PaddleOCR


def run_ocr():

    DICT_PATH = Path(
        r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\model\infer\python_ascii.txt"
    )

    # 1  create the pipeline
    ocr = PaddleOCR(use_textline_orientation=True, lang="en")
    # Path to your image
    json_path = Path(r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\model\Dataset\dev\pairs.json")

    try:

        with json_path.open(encoding="utf-8") as f:
            pairs = json.load(f)

        repo_root = json_path.parents[2]

        for pair in pairs:

            img_abs = (repo_root / pair["img_path"]).resolve()

            results = ocr.predict(str(img_abs))

            #print("Raw results:", results)  # Debug Line

            if results and isinstance(results, list) and len(results) > 0:
                # The new API returns a list with a dictionary containing rec_texts and rec_scores
                result_dict = results[0]

                rec_texts = result_dict['rec_texts']
                rec_scores = result_dict['rec_scores']
                line = ""
                for text in rec_texts:
                    line += text
                    line += " "
                print(f"{line, rec_scores}")
            else:
                print("No results returned or unexpected format")

    except Exception as e:
        print(f"Error with predict(): {e}")



if __name__ == "__main__":
    run_ocr()
