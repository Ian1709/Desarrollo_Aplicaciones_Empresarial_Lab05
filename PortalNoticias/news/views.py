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


def article_detail(request, pk):
    """Detalle de una noticia: imagen destacada, autor y categorías."""
    article = get_object_or_404(
        Article.objects.select_related('author').prefetch_related('categories'), pk=pk
    )
    return render(request, 'news/article_detail.html', {'article': article})
