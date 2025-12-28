from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from notebook.views import send_milvus
# FastAPI backend URL - adjust if needed
FASTAPI_URL = "http://localhost:8000"


def homepage(request):
    """
    Render the RAG homepage
    """
    context = {
        'page_title': 'RAG Knowledge Base',
        'api_url': FASTAPI_URL,
    }
    return render(request, 'RAG/homepage.html', context)


def search_view(request):
    """
    Search documents view
    """
    if request.method == 'POST':
        query = request.POST.get('query', '')
        top_k = int(request.POST.get('top_k', 5))
        
        try:
            response = requests.post(
                f"{FASTAPI_URL}/search",
                json={"text": query, "top_k": top_k},
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            context = {
                'query': query,
                'results': results.get('results', []),
                'page_title': 'Search Results'
            }
            return render(request, 'RAG/search_results.html', context)
        except requests.exceptions.RequestException as e:
            context = {
                'error': f"Error connecting to API: {str(e)}",
                'page_title': 'Search Documents'
            }
            return render(request, 'RAG/search.html', context)
    
    context = {'page_title': 'Search Documents'}
    return render(request, 'RAG/search.html', context)


def documents_view(request):
    """
    Manage documents view
    """
    try:
        # Get collection info
        response = requests.get(f"{FASTAPI_URL}/collection_info", timeout=10)
        response.raise_for_status()
        collection_info = response.json()
    except requests.exceptions.RequestException as e:
        collection_info = {'error': str(e)}
    
    context = {
        'collection_info': collection_info,
        'page_title': 'Manage Documents'
    }
    return render(request, 'RAG/documents.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_document(request):
    """
    Add a single document to the knowledge base
    """
    try:
        data = json.loads(request.body)
        doc_id = data.get('id')
        text = data.get('text')
        
        if not doc_id or not text:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing id or text'
            }, status=400)
        
        # Call FastAPI to add document
        response = requests.post(
            f"{FASTAPI_URL}/add_documents",
            json=[{"id": int(doc_id), "text": text}],
            timeout=30
        )
        response.raise_for_status()
        
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def add_documents_bulk(request):
    """
    Add multiple documents at once
    """
    try:
        data = json.loads(request.body)
        documents = data.get('documents', [])
        
        if not documents:
            return JsonResponse({
                'status': 'error',
                'message': 'No documents provided'
            }, status=400)
        
        # Call FastAPI to add documents
        response = requests.post(
            f"{FASTAPI_URL}/add_documents",
            json=documents,
            timeout=30
        )
        response.raise_for_status()
        
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """
    Chat endpoint - proxy to FastAPI
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        top_k = data.get('top_k', 3)
        
        if not question:
            return JsonResponse({
                'status': 'error',
                'message': 'Question is required'
            }, status=400)
        
        # Call FastAPI chat endpoint
        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={"question": question, "top_k": top_k},
            timeout=60
        )
        response.raise_for_status()
        
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': f"API Error: {str(e)}"
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def clear_collection(request):
    """
    Clear all documents from collection
    """
    try:
        response = requests.delete(f"{FASTAPI_URL}/clear_collection", timeout=30)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def collection_info_api(request):
    """
    Get collection statistics
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/collection_info", timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def api_status(request):
    """
    Check if FastAPI is running
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        response.raise_for_status()
        return JsonResponse({
            'status': 'online',
            'data': response.json()
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'offline',
            'message': str(e)
        }, status=503)


@csrf_exempt
@require_http_methods(["POST"])
def reset_data(request):
    """
    Chat endpoint - proxy to FastAPI
    """
    try:
        data = send_milvus(request)
        print(data)
        return JsonResponse({"status": "success"}, status=200)
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'status': 'error',
            'message': f"API Error: {str(e)}"
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
