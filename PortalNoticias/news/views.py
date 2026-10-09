from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def index(request):
    """Portada: las últimas noticias publicadas, de la más reciente a la más antigua."""
    articles = Article.objects.select_related('author').prefetch_related('categories')
    context = {
        'destacada': articles.first(),
        'articles': articles,
        'categories': Category.objects.all(),
    }
    return render(request, 'news/index.html', context)
