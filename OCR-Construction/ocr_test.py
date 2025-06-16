import numpy as np
from paddleocr import PaddleOCR


def run_ocr():

    # 1  create the pipeline
    ocr = PaddleOCR(use_textline_orientation=True, lang="en")
    # Path to your image
    image_path = r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\Dataset\148TT.png"  # change this to your actual image

    try:
        # Use the newer predict() method
        results = ocr.predict(image_path)

        if results and isinstance(results, list) and len(results) > 0:
            # The new API returns a list with a dictionary containing rec_texts and rec_scores
            result_dict = results[0]

            if 'rec_texts' in result_dict and 'rec_scores' in result_dict:
                rec_texts = result_dict['rec_texts']
                rec_scores = result_dict['rec_scores']

                print("Detected text:")
                for text, score in zip(rec_texts, rec_scores):
                    print(f"'{text}' (confidence: {score:.3f})")

                # Also print all detected text as a single block
                print("\nAll detected text:")
                for text in rec_texts:
                    print(text)

            else:
                print("No rec_texts found in results")
                print(f"Available keys: {list(result_dict.keys())}")
        else:
            print("No results returned or unexpected format")

    except Exception as e:
        print(f"Error with predict(): {e}")

        # Fallback to older method
        try:
            print("Trying fallback with ocr() method...")
            results = ocr.ocr(image_path)

            if results and results[0]:
                print("Detected text (fallback method):")
                for line in results[0]:
                    if line and len(line) >= 2 and len(line[1]) >= 2:
                        text = line[1][0]
                        confidence = line[1][1]
                        print(f"'{text}' (confidence: {confidence:.3f})")
            else:
                print("No text detected with fallback method.")

        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            print("Make sure the image path is correct and the image file exists.")



if __name__ == "__main__":
    run_ocr()
