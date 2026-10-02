"""Comprobación del panel de administración por HTTP (sin abrir el navegador).

Simula el inicio de sesión del superusuario con el cliente de pruebas de Django y
solicita las cuatro pantallas de listado y las cuatro de alta, que son las
"cuatro operaciones" que menciona el Paso 4 del enunciado.

Uso:  python evidencias/verificar_admin.py
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
from movies.models import Genre, Movie, Person, Rating  # noqa: E402

MODELOS = [
    ('Películas', Movie, 'movie'),
    ('Géneros', Genre, 'genre'),
    ('Personas', Person, 'person'),
    ('Valoraciones', Rating, 'rating'),
]


def main():
    User = get_user_model()
    admin_user = User.objects.get(username='admin')
    cliente = Client()
    ok_login = cliente.login(username='admin', password='admin123')

    print('ACCESO AL PANEL')
    print('-' * 60)
    print(f'  login superusuario "admin": {"OK" if ok_login else "FALLO"}')
    print(f'  GET /admin/ -> {cliente.get("/admin/").status_code}')

    print()
    print('CUATRO MODELOS REGISTRADOS (Paso 4: sin escribir ninguna vista)')
    print('-' * 60)
    from django.contrib import admin as dj_admin

    for etiqueta, modelo, slug in MODELOS:
        registrado = modelo in dj_admin.site._registry
        print(
            f'  {etiqueta:<13} registrado_en_admin={registrado}  '
            f'operaciones={modelo._meta.default_permissions}'
        )

    print()
    print('PANTALLAS DEL PANEL (listado / alta / edición)')
    print('-' * 60)
    for etiqueta, modelo, slug in MODELOS:
        listado = cliente.get(f'/admin/movies/{slug}/')
        alta = cliente.get(f'/admin/movies/{slug}/add/')
        edicion = cliente.get(f'/admin/movies/{slug}/1/change/')
        print(
            f'  {etiqueta:<13} /admin/movies/{slug}/ -> {listado.status_code}   '
            f'add/ -> {alta.status_code}   change/1/ -> {edicion.status_code}'
        )

    print()
    print('TOTAL DE MODELOS REGISTRADOS:', len(dj_admin.site._registry))


if __name__ == '__main__':
    main()
