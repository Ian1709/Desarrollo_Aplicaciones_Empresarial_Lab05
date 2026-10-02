"""Paso 9: qué desaparece del panel al entrar con la cuenta "editor".

Compara, con el cliente de pruebas de Django, lo que ve el superusuario (admin)
y lo que ve el usuario del grupo "editores" (editor):

- modelos que aparecen en el índice del panel
- acciones disponibles en el listado de películas
- botones y pantallas de borrado
- bloque de valoraciones (inline) dentro del formulario de la película

Uso:  python evidencias/verificar_permisos_editor.py
"""

import logging
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

# Los 403 del panel se muestran como código HTTP, no como excepción, y sin ruido
# por pantalla (logging silenciado solo en este script de evidencia).
logging.getLogger('django.request').setLevel(logging.CRITICAL)
logging.getLogger('django.security').setLevel(logging.CRITICAL)

CUENTAS = [('admin', 'admin123'), ('editor', 'editor123')]
RUTAS = [
    ('Géneros', '/admin/movies/genre/'),
    ('Personas', '/admin/movies/person/'),
    ('Valoraciones', '/admin/movies/rating/'),
    ('Películas (listado)', '/admin/movies/movie/'),
    ('Películas (alta)', '/admin/movies/movie/add/'),
]


def main():
    pelicula = Movie.objects.order_by('id').first()
    cambio = f'/admin/movies/movie/{pelicula.pk}/change/'
    borrado = f'/admin/movies/movie/{pelicula.pk}/delete/'

    print('PASO 9 - COMPARATIVA SUPERUSUARIO vs USUARIO EDITOR')
    print('=' * 78)

    for usuario, clave in CUENTAS:
        cliente = Client(raise_request_exception=False)
        cliente.login(username=usuario, password=clave)
        User = get_user_model()
        cuenta = User.objects.get(username=usuario)
        print()
        print(f'CUENTA: {usuario}  (is_superuser={cuenta.is_superuser}, grupos='
              f'{list(cuenta.groups.values_list("name", flat=True))})')
        print('-' * 78)
        print('  Permisos efectivos:')
        for permiso in sorted(cuenta.get_all_permissions()):
            print(f'    {permiso}')
        print()
        print('  Pantallas del panel (código HTTP):')
        for etiqueta, ruta in RUTAS:
            print(f'    {etiqueta:<24} {ruta:<32} -> {cliente.get(ruta).status_code}')
        print()
        print(f'  Formulario de película {cambio} -> {cliente.get(cambio).status_code}')
        print(f'  Pantalla de borrado    {borrado} -> {cliente.get(borrado).status_code}')

        respuesta_listado = cliente.get('/admin/movies/movie/')
        html_listado = respuesta_listado.content.decode()
        print(f'  acción "Eliminar seleccionados" en el listado: '
              f'{"delete_selected" in html_listado}')
        print(f'  casilla de selección de acciones (action_checkbox): '
              f'{"action-checkbox" in html_listado}')

        respuesta_cambio = cliente.get(cambio)
        html_cambio = respuesta_cambio.content.decode()
        print(f'  botón "Eliminar" en el formulario de la película: '
              f'{"deletelink" in html_cambio}')
        print(f'  ¿aparece el bloque de valoraciones (inline)?: '
              f'{"valoraciones" in html_cambio.lower()}')
        print(f'  ¿se ven los campos de auditoría en solo lectura?: '
              f'{"fecha_creacion" in html_cambio}')

        indice = cliente.get('/admin/')
        html_indice = indice.content.decode()
        print('  Modelos visibles en el índice del panel:')
        for etiqueta, slug in [
            ('Películas', 'movie'),
            ('Géneros', 'genre'),
            ('Personas', 'person'),
            ('Valoraciones', 'rating'),
        ]:
            visible = f'/admin/movies/{slug}/' in html_indice
            print(f'    {etiqueta:<13} visible={visible}')

    print()
    print('=' * 78)
    print('CONCLUSIÓN')
    print('-' * 78)
    print('  Con el superusuario se ven los cuatro modelos, se puede añadir, cambiar')
    print('  y eliminar, y aparece el bloque de valoraciones dentro de la película.')
    print('  Con el usuario "editor" desaparecen: los otros tres modelos del índice,')
    print('  la acción/botón de eliminar (HTTP 403) y el inline de valoraciones, porque')
    print('  el grupo "editores" solo tiene add/change/view sobre Movie y ningún')
    print('  permiso sobre Genre, Person ni Rating.')


if __name__ == '__main__':
    main()