import cv2
import os
from PIL import Image, ImageEnhance
import numpy as np
import pytesseract

# — If tesseract.exe isn’t on your PATH, uncomment and update this:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def check_image_properties(image_path):
    """Check resolution and DPI of an image"""
    img = Image.open(image_path)
    width, height = img.size

    # Get DPI (dots per inch) - defaults to 72 if not set
    dpi = img.info.get('dpi')
    if isinstance(dpi, tuple):
        dpi_x, dpi_y = dpi
    else:
        dpi_x = dpi_y = dpi

    print(f"Image dimensions: {width} x {height} pixels")
    print(f"DPI: {dpi_x} x {dpi_y}")
    print(f"Physical size: {width/dpi_x:.2f} x {height/dpi_y:.2f} inches")

    return(height, width)


def scaling(image_path) -> str:

     ranges = {"min": 800*600, "good": 1200*900, "optimal_min": 1600*1200,
               "optimal_max": 2400*1800, "over-kill": 3000*3000}

     height, width = check_image_properties(image_path)
     pixels = height * width
     img_curr = cv2.imread(image_path)

     if pixels < ranges["min"]:

         print(f"Upscaling image...")
         img_scaled = cv2.resize(img_curr, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

         # Save directly in Dataset folder with modified name
         base_name = os.path.splitext(image_path)[0]  # Remove extension
         output_path = f"{base_name}_upscaled.png"
         cv2.imwrite(output_path, img_scaled)
         print(f"Saved: {output_path}")
         return output_path


     elif pixels > ranges["over-kill"]:

         print(f"Downscaling image...")
         img_scaled = cv2.resize(img_curr, None, fx=0.67, fy=0.67, interpolation=cv2.INTER_AREA)

         base_name = os.path.splitext(image_path)[0]
         output_path = f"{base_name}_downscaled.png"
         cv2.imwrite(output_path, img_scaled)
         print(f"Saved: {output_path}")
         return output_path

     else:
         print("No scaling needed.")
         return image_path


def ocr_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img, lang="eng")

if __name__ == "__main__":
    # put a sample scan image in this folder (e.g. scan.png)
    path = r"C:\Users\sarfr\Documents\dev-orig\paper-code-scanner\Dataset\148 TT.png"
    print("Resolution:\n" + "*"*40)
    print(check_image_properties(path))

    new_path = scaling(path)

    print("OCR result:\n" + "-"*40)
    print(ocr_image(new_path))
    print("-"*40)
