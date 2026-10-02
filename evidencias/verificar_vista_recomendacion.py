"""Paso 10: comprobación de la vista pública de recomendación.

Imprime, con los datos cargados en el Paso 8, qué recomienda la vista para cada
género y para cada película, y comprueba el SQL que Django genera.

Uso:  python evidencias/verificar_vista_recomendacion.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab05_proyecto.settings')

import django  # noqa: E402

django.setup()

from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from movies.models import Genre, Movie  # noqa: E402
from movies.views import mejores_por_genero, recommender  # noqa: E402

setup_test_environment()


def main():
    cliente = Client()

    print('PASO 10 - VISTA PÚBLICA DE RECOMENDACIÓN')
    print('-' * 70)
    print(f'  películas en la base de datos: {Movie.objects.count()}')
    print(f'  géneros: {Genre.objects.count()}')
    print()

    print('RECOMENDACIÓN POR GÉNERO (mejores_por_genero)')
    print('-' * 70)
    for genero, peliculas in mejores_por_genero():
        linea = ', '.join(f'{p.titulo} ({p.media:.2f})' for p in peliculas)
        print(f'  {genero.nombre:<18} -> {linea}')
    print()

    print('RECOMENDACIONES DESDE LA FICHA DE CADA PELÍCULA (recommender)')
    print('-' * 70)
    for pelicula in Movie.objects.prefetch_related('generos').order_by('titulo'):
        generos = ', '.join(g.nombre for g in pelicula.generos.all())
        recomendadas = recommender(pelicula)
        detalle = ', '.join(f'{p.titulo} ({p.media:.2f})' for p in recomendadas) or '—'
        print(f'  {pelicula.titulo} [{generos or "sin género"}]')
        print(f'      -> {detalle}')
    print()

    print('PÁGINAS PÚBLICAS QUE RESPONDEN')
    print('-' * 70)
    for etiqueta, ruta in [
        ('Catálogo', '/'),
        ('Ficha de Inception', f'/pelicula/{Movie.objects.get(titulo="Inception").pk}/'),
        ('Ficha inexistente', '/pelicula/999999/'),
    ]:
        respuesta = cliente.get(ruta)
        print(f'  {etiqueta:<20} {ruta:<26} -> {respuesta.status_code}')
    print()

    print('SQL DE LA RECOMENDACIÓN (consulta generada por Django)')
    print('-' * 70)
    pelicula = Movie.objects.get(titulo='Inception')
    consulta = recommender(pelicula)
    print(str(consulta.query))
    print()
    print('CONCLUSIÓN')
    print('-' * 70)
    print('  El panel de administración (Pasos 4-9) permite mantener los datos, pero')
    print('  no sabe responder "¿qué me recomiendas?": ordenar por valoración media y')
    print('  relate peliculas del mismo género exige una vista propia (views + urls +')
    print('  plantilla), tal y como se ve en las páginas públicas de arriba.')


if __name__ == '__main__':
    main()