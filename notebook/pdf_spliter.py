import fitz,pymupdf
import os
from default_dir import *

def pdf_slicing(file_path):
    zoom_x = 4.0
    zoom_y = 4.0
    mat = pymupdf.Matrix(zoom_x, zoom_y)
    doc = fitz.open(file_path)
    # print(doc.page_count)
    # check the ./temp/ is empty or not first
    if (os.listdir(SAVE_IMAGE_DIR)):
        try:
            for old_file in os.listdir(SAVE_IMAGE_DIR):
                os.remove(SAVE_IMAGE_DIR + old_file)
        except Exception as e:
            print("Error while trying to cleanup temp : ", e)

    for page_num in range(doc.page_count):
        if page_num == 10:
            break
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        output_img_path = os.path.join(
            SAVE_IMAGE_DIR,
            f"page_{page_num:04d}.png"
        )

        pix.save(output_img_path)
        print(f"Saved: {output_img_path}")

# pdf_slicing(r"./data/xulytinhieu.pdf")