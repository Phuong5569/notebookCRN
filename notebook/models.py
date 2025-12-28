from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Page(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')
    image = models.ImageField(upload_to='pages/')
    extracted_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Page {self.id} of {self.book.title}"
