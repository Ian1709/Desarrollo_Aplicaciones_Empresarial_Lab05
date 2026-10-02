"""Comprobación de la personalización del panel (Pasos 5, 6 y 7).

Usa el cliente de pruebas de Django con la sesión del superusuario y lee el
`ChangeList` que el propio admin construye para las pantallas de listado:
columnas mostradas, filtros de la barra lateral y campos de búsqueda.

Uso:  python evidencias/verificar_admin_personalizado.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab05_proyecto.settings')

import django  # noqa: E402

django.setup()

from django.contrib import admin as dj_admin  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from movies.models import Genre, Movie, Person, Rating  # noqa: E402

# Necesario para que el cliente de pruebas capture el contexto de las plantillas
# (permite leer el ChangeList que construye el propio panel).
setup_test_environment()

MODELOS = [
    ('Películas', Movie, 'movie'),
    ('Géneros', Genre, 'genre'),
    ('Personas', Person, 'person'),
    ('Valoraciones', Rating, 'rating'),
]


def describe_list_display(resp):
    etiquetas = []
    for campo in resp.context['cl'].list_display:
        short = getattr(campo, 'short_description', None)
        etiquetas.append(short if short else str(campo))
    return etiquetas


def describe_filters(resp):
    filtros = []
    for spec in resp.context['cl'].filter_specs:
        titulo = getattr(spec, 'title', None)
        if titulo is None:
            titulo = getattr(getattr(spec, 'field', None), 'verbose_name', str(spec))
        filtros.append(str(titulo))
    return filtros


def main():
    cliente = Client()
    cliente.login(username='admin', password='admin123')

    print('PASO 5 - CONFIGURACION DECLARADA EN admin.py')
    print('-' * 60)
    for etiqueta, modelo, slug in MODELOS:
        admin_modelo = dj_admin.site._registry[modelo]
        filtros = [f.__name__ if hasattr(f, 'lookups') else str(f) for f in admin_modelo.list_filter]
        print(f'  {etiqueta} ({modelo.__name__}Admin)')
        print(f'    list_display : {list(admin_modelo.list_display)}')
        print(f'    list_filter  : {filtros}')
        print(f'    search_fields: {list(admin_modelo.search_fields)}')

    print()
    print('PASO 5 - COLUMNAS Y FILTOS QUE PINTA EL PANEL')
    print('-' * 60)
    for etiqueta, modelo, slug in MODELOS:
        resp = cliente.get(f'/admin/movies/{slug}/')
        print(f'  {etiqueta}  (HTTP {resp.status_code})')
        print(f'    list_display : {describe_list_display(resp)}')
        print(f'    filtros barra: {describe_filters(resp)}')
        print(f'    search_fields: {[str(f) for f in resp.context["cl"].search_fields]}')
        print()

    print('BUSQUEDA Y FILTROS DESDE EL PANEL (parámetros de la URL)')
    print('-' * 60)
    for termino in ('matrix', 'godfather'):
        resp = cliente.get('/admin/movies/movie/', {'q': termino})
        print(f'  ?q={termino} -> {resp.context["cl"].result_count} película(s)')
    for decada in ('2020', '2010', '2000'):
        resp = cliente.get('/admin/movies/movie/', {'decada': decada})
        print(f'  ?decada={decada} -> {resp.context["cl"].result_count} película(s)')
    for genero in Genre.objects.all()[:6]:
        resp = cliente.get('/admin/movies/movie/', {'generos__id__exact': genero.pk})
        print(
            f'  ?generos__id__exact={genero.pk} ({genero.nombre}) -> '
            f'{resp.context["cl"].result_count} película(s)'
        )

    print()
    print('PASO 6 - INLINE DE VALORACIONES EN EL FORMULARIO DE LA PELÍCULA')
    print('-' * 60)
    pelicula = Movie.objects.first()
    if pelicula:
        resp = cliente.get(f'/admin/movies/movie/{pelicula.pk}/change/')
        formset = resp.context['inline_admin_formsets'][0]
        forms = formset.formset
        print(f'  película abierta: {pelicula}')
        print(f'  inline: {formset.opts.__class__.__name__} -> modelo {formset.opts.model.__name__}')
        print(f'  campos del inline: {[f for f in formset.form.fields if f != "id"]}')
        print(f'  líneas iniciales (valoraciones existentes): {forms.initial_form_count()}')
        print(f'  líneas extra para añadir sin salir del registro: {forms.total_form_count() - forms.initial_form_count()}')
        print(f'  valoraciones guardadas en BD: {pelicula.valoraciones.count()}')
    else:
        print('  (aún no hay películas: se crean en el Paso 8)')

    print()
    print('PASO 7 - CAMPOS DE AUDITORÍA EN SOLO LECTURA')
    print('-' * 60)
    if pelicula:
        resp = cliente.get(f'/admin/movies/movie/{pelicula.pk}/change/')
        form = resp.context['adminform'].form
        auditoria = ('fecha_creacion', 'fecha_modificacion')
        print(f'  campos editables del formulario: {sorted(form.fields)}')
        print(f'  campos NO editables: {[c for c in auditoria if c not in form.fields]}')
        html = resp.content.decode()
        print(f'  el HTML sigue mostrando la fecha de creación: {"fecha_creacion" in html}')


if __name__ == '__main__':
    main()
