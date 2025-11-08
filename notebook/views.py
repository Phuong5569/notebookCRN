# from django.shortcuts import render
# from django.http import HttpResponse
# from django.template import loader
# # Create your views here.

# def notebook(request):
#     template = loader.get_template("notebook-canvas.html")
#     return HttpResponse(template.render())

from django.views.decorators.http import require_POST
import json
import base64
import os
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from notebook.RCNNMdoels import *
from notebook.utils import create_new_book
from datetime import date 
from django.utils.timezone import now
import shutil
import uuid
from notebook.NLPprocess import *

@csrf_exempt
def homepage(request):
    return render(request, 'notebook/homepage.html')

@csrf_exempt
def notebook_canvas(request):
    return render(request, 'notebook/notebook-canvas.html')


@csrf_exempt
@require_http_methods(["POST"])
def save_notebook_lines(request):
    """Save individual notebook lines as separate image files"""
    try:
        data = json.loads(request.body)
        images = data.get('images', [])
        
        if not images:
            return JsonResponse({'error': 'No images provided'}, status=400)
        
        # Create a unique folder for this notebook session
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"notebook_lines_{timestamp}_{session_id}"
        
        # Create the folder path in the project directory
        project_root = settings.BASE_DIR
        notebook_lines_path = os.path.join(project_root, 'notebook_lines')
        base_path = os.path.join(notebook_lines_path, folder_name)
        
        # Create directories if they don't exist
        os.makedirs(base_path, exist_ok=True)
        
        saved_files = []
        
        for image_data in images:
            line_number = image_data.get('lineNumber')
            data_url = image_data.get('dataURL')
            
            if not data_url or not data_url.startswith('data:image/png;base64,'):
                continue
            
            # Extract base64 data
            base64_data = data_url.split(',')[1]
            image_content = base64.b64decode(base64_data)
            
            line_number = image_data.get('lineNumber')

            if line_number is None:
                continue

            try:
                line_number = int(line_number)
            except ValueError:
                continue

            filename = f"line_{line_number:03d}.png"
            
            
            file_path = os.path.join(base_path, filename)
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(image_content)
            
            saved_files.append({
                'line_number': line_number,
                'filename': filename,
                'path': file_path
            })

        
        return JsonResponse({
            'success': True,
            'message': f'Successfully saved {len(saved_files)} line images',
            'folder': folder_name,
            'folder_path': base_path,
            'files': saved_files,
            'session_id': session_id,
            'timestamp': timestamp
        })
        
    except Exception as e:
        print(str(e))
        return JsonResponse({
            'error': f'Failed to save images: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def extract_text_from_lines(request):
    """Extract text from all line images and return as downloadable text file"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        timestamp = data.get('timestamp')
        
        if not session_id or not timestamp:
            return JsonResponse({'error': 'Session ID and timestamp required'}, status=400)
        
        # Construct folder path
        folder_name = f"notebook_lines_{timestamp}_{session_id}"
        project_root = settings.BASE_DIR
        notebook_lines_path = os.path.join(project_root, 'notebook_lines')
        base_path = os.path.join(notebook_lines_path, folder_name)
        
        if not os.path.exists(base_path):
            return JsonResponse({'error': 'Image folder not found'}, status=404)
        
        # Load the OCR model
        try:
            model = Model(inputs, outputs)
            
            # Load model weights - Update this path to your model file
            weights_path = os.path.join(settings.BASE_DIR, 'model_checkpoint_weights.hdf5')
            if not os.path.exists(weights_path):
                return JsonResponse({'error': 'OCR model weights not found. Please place model_checkpoint_weights.hdf5 in your project root.'}, status=404)
            
            model.load_weights(weights_path)
        except Exception as e:
            return JsonResponse({'error': f'Failed to load OCR model: {str(e)}'}, status=500)
        
        # Get all line images and sort them
        image_files = []
        for filename in os.listdir(base_path):
            if filename.startswith('line_') and filename.endswith('.png'):
                image_files.append(filename)
        
        image_files.sort()  # Sort to ensure correct order
        
        if not image_files:
            return JsonResponse({'error': 'No line images found'}, status=404)
        
        # Extract text from each line
        extracted_lines = []
        for filename in image_files:
            image_path = os.path.join(base_path, filename)
            line_text = extract_text_from_image(image_path, model, char_list)
            
            # Only add non-empty lines
            if line_text.strip():
                extracted_lines.append(line_text)
        
        # Combine all lines into a single text
        full_text = ' '.join(extracted_lines)
        print("Original Text : ",full_text)
        print("_______________________________________process ViT correction_______________________________________")
        full_text = correct_ocr(full_text)
        print("_______________________________________DONE ViT correction_______________________________________")
        print("Text after correction : ",full_text)
        if not full_text.strip():
            return JsonResponse({'error': 'No text could be extracted from the images'}, status=404)
        
        # Create response with the text file
        response = HttpResponse(full_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="extracted_text_{timestamp}_{session_id}.txt"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to extract text: {str(e)}'
        }, status=500)
        

@csrf_exempt
def create_book(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_title = data.get("title")
        if not book_title:
            return JsonResponse({"error": "Title is required"}, status=400)
        
        result, status = create_new_book(book_title)
        return JsonResponse(result, status=status)


def list_books(request):
    books = []
    base_path = settings.BOOK_STORAGE_DIR
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        json_path = os.path.join(folder_path, "data.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    book_data = json.load(f)
                    books.append(book_data)
                except Exception as e:
                    continue  # skip corrupted file
    return JsonResponse({"books": books})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_book(request, book_id):
    """
    Deletes an entire book folder and its contents.
    URL: DELETE /api/book/<book_id>/delete/
    """
    # Path to the book folder
    book_dir = os.path.join(settings.BOOK_STORAGE_DIR, book_id)

    if not os.path.isdir(book_dir):
        return JsonResponse({"error": "Book not found"}, status=404)

    # Remove the entire directory
    try:
        shutil.rmtree(book_dir)
    except Exception as e:
        return JsonResponse({"error": f"Could not delete book: {e}"}, status=500)

    return JsonResponse({"status": "deleted", "book_id": book_id})


def load_book_data(request, book_id):
    book_dir = os.path.join(settings.BOOK_STORAGE_DIR, book_id)
    data_file = os.path.join(book_dir, 'data.json')

    if not os.path.exists(data_file):
        return HttpResponseNotFound('Book not found.')

    with open(data_file, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    
    return JsonResponse(book_data)

@csrf_exempt
@require_POST
def save_page(request, book_id):
    try:
        data = json.loads(request.body.decode("utf-8"))
        page_id = str(data.get("page_id"))
        image_data = data.get("image_data")

        if not page_id or not image_data:
            return JsonResponse({"error": "Missing page_id or image_data"}, status=400)

        # Path to book folder
        book_dir = os.path.join(settings.BOOK_STORAGE_DIR, book_id)
        os.makedirs(book_dir, exist_ok=True)

        # Save page image
        image_path = os.path.join(book_dir, f"page-{page_id}.png")
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data.split(",")[1]))

        # Update data.json
        data_json_path = os.path.join(book_dir, "data.json")

        if os.path.exists(data_json_path):
            with open(data_json_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {
                "id": book_id,
                "title": book_id,
                "created_at": now().date().isoformat(),
                "last_modified": now().date().isoformat(),
                "pages": []
            }

        if "pages" not in metadata:
            metadata["pages"] = []

        # Avoid duplicates
        if page_id not in metadata["pages"]:
            metadata["pages"].append(page_id)

        metadata["last_modified"] = now().date().isoformat()

        with open(data_json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return JsonResponse({"status": "saved", "page": page_id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_page(request, book_id, page_id):
    book_dir = os.path.join(settings.BOOK_STORAGE_DIR, book_id)
    image_path = os.path.join(book_dir, f"page-{page_id}.png")
    data_path = os.path.join(book_dir, "data.json")

    if not os.path.exists(data_path):
        return JsonResponse({"error": "Book not found"}, status=404)

    # Delete image
    if os.path.exists(image_path):
        os.remove(image_path)

    # Update data.json
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "pages" in data:
        data["pages"] = [pid for pid in data["pages"] if str(pid) != str(page_id)]

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({"status": "deleted", "page_id": page_id})

@csrf_exempt
@require_http_methods(["POST"])
@csrf_exempt
@require_http_methods(["POST"])
def rename_book(request, book_id):
    try:
        data = json.loads(request.body)
        new_title = data.get("new_title", "").strip()
        if not new_title:
            return JsonResponse({"error": "New title is required"}, status=400)

        book_dir = os.path.join(settings.BOOK_STORAGE_DIR, book_id)
        if not os.path.exists(book_dir):
            return JsonResponse({"error": "Book not found"}, status=404)

        data_json = os.path.join(book_dir, "data.json")
        if os.path.exists(data_json):
            with open(data_json, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {}

        metadata["title"] = new_title
        metadata["last_modified"] = datetime.now().date().isoformat()

        with open(data_json, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return JsonResponse({
            "success": True,
            "id": book_id,  # unchanged
            "title": new_title
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
