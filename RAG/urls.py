from django.urls import path
from . import views

app_name = 'RAG'

urlpatterns = [
    # Main pages
    path('', views.homepage, name='homepage'),
    path('search/', views.search_view, name='search'),
    path('documents/', views.documents_view, name='documents'),
    path('reset_data/', views.reset_data, name='reset_data'),
    
    # API endpoints (proxy to FastAPI)
    path('api/chat/', views.chat_api, name='api_chat'),
    path('api/add-document/', views.add_document, name='api_add_document'),
    path('api/add-documents-bulk/', views.add_documents_bulk, name='api_add_documents_bulk'),
    path('api/clear-collection/', views.clear_collection, name='api_clear_collection'),
    path('api/collection-info/', views.collection_info_api, name='api_collection_info'),
    path('api/status/', views.api_status, name='api_status'),
]