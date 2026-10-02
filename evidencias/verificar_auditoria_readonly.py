"""Paso 7: los campos de auditoría de la película no se pueden editar en el panel.

Comprueba tres cosas sobre /admin/movies/movie/<id>/change/:
  1. `fecha_creacion` y `fecha_modificacion` NO aparecen como campos del formulario.
  2. El HTML sí las muestra (se muestran, pero en solo lectura).
  3. Un POST que intenta cambiar esas fechas no las modifica (auto_now_add/auto_now).

Uso:  python evidencias/verificar_auditoria_readonly.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab05_proyecto.settings')

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from movies.models import Movie  # noqa: E402

setup_test_environment()

TITULO_TEMPORAL = 'PELICULA TEMPORAL PARA COMPROBAR SOLO LECTURA'


def main():
    cliente = Client()
    cliente.login(username='admin', password='admin123')

    pelicula = Movie.objects.filter(titulo=TITULO_TEMPORAL).first()
    creada = False
    if pelicula is None:
        pelicula = Movie.objects.create(titulo=TITULO_TEMPORAL, anio=2000, sinopsis='temporal')
        creada = True

    print('PASO 7 - CAMPOS DE AUDITORÍA EN SOLO LECTURA')
    print('-' * 60)
    print(f'  película de prueba: {pelicula} (id={pelicula.pk})')
    print(f'  fecha_creacion en BD: {pelicula.fecha_creacion}')
    print(f'  fecha_modificacion en BD: {pelicula.fecha_modificacion}')

    resp = cliente.get(f'/admin/movies/movie/{pelicula.pk}/change/')
    form = resp.context['adminform'].form
    print()
    print(f'  GET change/ -> {resp.status_code}')
    print(f'  campos editables del formulario: {sorted(form.fields)}')
    print(
        '  auditoría ausente del formulario (solo lectura): '
        f'{[c for c in ("fecha_creacion", "fecha_modificacion") if c not in form.fields]}'
    )
    html = resp.content.decode()
    print(f'  la fecha de creación se sigue mostrando en el HTML: {"fecha_creacion" in html}')
    print(f'  la fecha de modificación se sigue mostrando en el HTML: {"fecha_modificacion" in html}')

    # Intento de manipulating por POST (los campos readonly ni siquiera llegan al formulario)
    datos = {
        'titulo': pelicula.titulo,
        'anio': pelicula.anio,
        'sinopsis': pelicula.sinopsis,
        'generos': [],
        'directores': [],
        'valoraciones-TOTAL_FORMS': '0',
        'valoraciones-INITIAL_FORMS': '0',
        'valoraciones-MIN_NUM_FORMS': '0',
        'valoraciones-MAX_NUM_FORMS': '1000',
        'fecha_creacion': '2000-01-01 00:00:00',
        'fecha_modificacion': '2000-01-01 00:00:00',
        '_continue': '1',
    }
    resp = cliente.post(f'/admin/movies/movie/{pelicula.pk}/change/', datos, follow=True)
    pelicula.refresh_from_db()
    print()
    print(f'  POST con fechas falsas -> {resp.status_code}')
    print(f'  fecha_creacion tras el POST: {pelicula.fecha_creacion}')
    print(f'  fecha_modificacion tras el POST: {pelicula.fecha_modificacion}')
    cambio = (
        pelicula.fecha_creacion.year == 2000
        or pelicula.fecha_modificacion.year == 2000
    )
    print(f'  ¿alguna fecha fue alterada por el formulario?: {"SÍ (mal)" if cambio else "NO (correcto)"}')

    if creada:
        pelicula.delete()
        print()
        print('  (la película temporal de la prueba se ha borrado)')

    # El usuario final que se documenta en el entregable
    User = get_user_model()
    print()
    print(f'  superusuario en la base de datos: {User.objects.get(username="admin").username}')


if __name__ == '__main__':
    main()
