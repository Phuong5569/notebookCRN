import os
import json
from django.conf import settings
from datetime import datetime

def list_books():
    base = settings.BOOK_STORAGE_DIR
    return [name for name in os.listdir(base) if os.path.isdir(os.path.join(base, name))]

def load_book(book_name):
    book_path = os.path.join(settings.BOOK_STORAGE_DIR, book_name, 'data.json')
    if os.path.exists(book_path):
        with open(book_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_book(book_name, data):
    folder = os.path.join(settings.BOOK_STORAGE_DIR, book_name)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_new_book(book_title):
    # Create folder name from title (simple slug)
    folder_name = book_title.strip().lower().replace(' ', '-')
    book_dir = os.path.join(settings.BOOK_STORAGE_DIR, folder_name)

    if os.path.exists(book_dir):
        return {'error': 'Book already exists'}, 400

    os.makedirs(book_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    # Final book metadata structure
    metadata = {
        "id": folder_name,
        "title": book_title,
        "created_at": today,
        "last_modified": today,
        "context": "",
        "pages": []
    }

    with open(os.path.join(book_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return metadata, 200