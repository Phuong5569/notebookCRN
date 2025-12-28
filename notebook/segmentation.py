import cv2
import numpy as np
import os
from datetime import datetime
import shutil

def sort_contours_reading_order(contours, y_tolerance=20):
    boxes = [cv2.boundingRect(c) for c in contours]
    contours_with_boxes = list(zip(contours, boxes))

    # sort top to bottom
    contours_with_boxes.sort(key=lambda b: b[1][1])

    lines = []
    for c, (x, y, w, h) in contours_with_boxes:
        placed = False
        for line in lines:
            _, (lx, ly, lw, lh) = line[0]
            if abs(y - ly) < y_tolerance:
                line.append((c, (x, y, w, h)))
                placed = True
                break
        if not placed:
            lines.append([(c, (x, y, w, h))])

    # sort each line left -> right
    sorted_contours = []
    for line in lines:
        line.sort(key=lambda b: b[1][0])
        sorted_contours.extend([c for c, _ in line])

    return sorted_contours


def segmenter(img, output_dir, line_counter_start=1):
    """
    Segment an image into lines and save them
    Returns the number of lines found
    """
    kernel = np.ones((3, 85), np.uint8)
    dilated = cv2.dilate(cv2.bitwise_not(img), kernel, iterations=1)
    (contours, hierarchy) = cv2.findContours(
        dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    contours = sort_contours_reading_order(contours)
    
    counter = line_counter_start
    for ctr in contours:
        if cv2.contourArea(ctr) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(ctr)
        line = img[y:(y+h), x:(x+w)]
        
        # Save with the exact naming format: line_1.png, line_2.png, etc.
        filename = f"line_{counter}.png"
        cv2.imwrite(os.path.join(output_dir, filename), line)
        counter += 1
    
    return counter - line_counter_start


def segment_book_lines(book_id, media_root, base_dir):
    """
    Segment all pages of a book into individual lines
    Saves in format: notebook_lines/notebook_lines_{timestamp}_{session_id}/line_X.png
    
    This matches the format expected by extract_text_from_lines()
    """
    # Generate session info
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = datetime.now().strftime('%f')  # microseconds for uniqueness
    
    # Create output directory in the same format as before
    folder_name = f"notebook_lines_{timestamp}_{session_id}"
    notebook_lines_path = os.path.join(base_dir, 'notebook_lines')
    output_dir = os.path.join(notebook_lines_path, folder_name)
    
    # Clean up and create fresh directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all page images from book storage
    book_storage_dir = os.path.join(media_root, 'book_storage', book_id)
    
    if not os.path.exists(book_storage_dir):
        raise ValueError(f"Book storage directory not found: {book_storage_dir}")
    
    page_files = sorted([
        f for f in os.listdir(book_storage_dir) 
        if f.startswith('page-') and f.endswith('.png')
    ])
    
    if not page_files:
        raise ValueError(f"No page images found in {book_storage_dir}")
    
    # Process all pages and save lines sequentially with continuous numbering
    total_lines = 0
    line_counter = 1  # Start from 1, continuous across all pages
    
    for page_file in page_files:
        page_path = os.path.join(book_storage_dir, page_file)
        
        # Read image in grayscale
        img = cv2.imread(page_path, 0)
        if img is None:
            print(f"Warning: Could not read {page_path}")
            continue
        
        # Segment this page and save lines directly to output_dir
        lines_found = segmenter(img, output_dir, line_counter)
        line_counter += lines_found
        total_lines += lines_found
    
    return {
        'session_id': session_id,
        'timestamp': timestamp,
        'total_lines': total_lines,
        'page_count': len(page_files),
        'output_path': output_dir,
        'folder_name': folder_name
    }