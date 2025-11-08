from django.urls import path
from . import views

app_name = 'notebook'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('save-lines/', views.save_notebook_lines, name='save_notebook_lines'),
    path('extract-text/', views.extract_text_from_lines, name='extract_text_from_lines'),
    path('create-book/', views.create_book, name='create-book'),
    path("api/books/", views.list_books, name="list_books"),
    path('api/book/<str:book_id>/delete/', views.delete_book, name='delete_book'),
    path('api/book/<str:book_id>/', views.load_book_data),
    path('api/book/<str:book_id>/save-page/', views.save_page),
    path('notebook-canvas/', views.notebook_canvas, name='notebook_canvas'),
    path("api/book/<str:book_id>/page/<str:page_id>/delete/", views.delete_page, name="delete_page"),
    path("api/book/<str:book_id>/rename/", views.rename_book),
]
