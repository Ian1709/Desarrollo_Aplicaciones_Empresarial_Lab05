"""Paso 10: vista pública de recomendación de películas del mismo género mejor valoradas.

El panel de administración sirve para mantener los datos, pero no puede responder
a la pregunta "¿qué me recomiendas?": esa lógica de negocio necesita una vista
propia, sus URL y sus plantillas.
"""

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie


def movie_list(request):
    """Catálogo público: todas las películas con su media de valoraciones."""
    peliculas = (
        Movie.objects.annotate(
            media=Avg('valoraciones__puntuacion'),
            num_valoraciones=Count('valoraciones', distinct=True),
        )
        .prefetch_related('generos', 'directores')
        .order_by('-media', '-anio', 'titulo')
    )
    return render(
        request,
        'movies/movie_list.html',
        {
            'peliculas': peliculas,
            'generos': Genre.objects.all(),
            'mejores_por_genero': mejores_por_genero(),
        },
    )


def movie_detail(request, pk):
    """Ficha de una película con sus valoraciones y recomendaciones similares."""
    pelicula = get_object_or_404(
        Movie.objects.prefetch_related('generos', 'directores', 'valoraciones'), pk=pk
    )
    genero_principal = pelicula.generos.first()
    recomendaciones = recommender(pelicula)
    return render(
        request,
        'movies/movie_detail.html',
        {
            'pelicula': pelicula,
            'genero_principal': genero_principal,
            'recomendaciones': recomendaciones,
        },
    )


def mejores_por_genero(limite=3):
    """Para cada género, las `limite` películas mejor valoradas (la "recomendación")."""
    recomendacion = []
    for genero in Genre.objects.all():
        peliculas = (
            Movie.objects.filter(generos=genero)
            .annotate(
                media=Avg('valoraciones__puntuacion'),
                num_valoraciones=Count('valoraciones', distinct=True),
            )
            .filter(num_valoraciones__gt=0)
            .order_by('-media', '-anio')[:limite]
        )
        if peliculas:
            recomendacion.append((genero, peliculas))
    return recomendacion


def recommender(pelicula, limite=5):
    """Películas que comparten al menos un género con `pelicula`, mejor valoradas.

    Usa `generos__in` (doble guion) sobre la relación muchos a muchos y excluye
    la propia película. Solo devuelve películas con valoraciones.
    """
    generos = list(pelicula.generos.values_list('id', flat=True))
    if not generos:
        return Movie.objects.none()
    return (
        Movie.objects.filter(generos__in=generos)
        .exclude(pk=pelicula.pk)
        .annotate(
            media=Avg('valoraciones__puntuacion'),
            num_valoraciones=Count('valoraciones', distinct=True),
        )
        .filter(num_valoraciones__gt=0)
        .prefetch_related('generos')
        .distinct()
        .order_by('-media', '-num_valoraciones', '-anio')[:limite]
    )