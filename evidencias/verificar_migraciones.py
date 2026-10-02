"""Verificación del Paso 3: superusuario creado y tablas generadas por la migración.

Uso:  python evidencias/verificar_migraciones.py
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
from django.db import connection  # noqa: E402

User = get_user_model()

print('SUPERUSUARIO CREADO (Paso 3)')
print('-' * 60)
for u in User.objects.filter(is_superuser=True):
    print(f'  username={u.username}  email={u.email}  is_staff={u.is_staff}  is_superuser={u.is_superuser}')

print()
print('TABLAS CREADAS EN SQLite')
print('-' * 60)
with connection.cursor() as cur:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'movies%' ORDER BY name")
    for (name,) in cur.fetchall():
        print(f'  {name}')

print()
print('DETALLE movies_movie')
print('-' * 60)
with connection.cursor() as cur:
    cur.execute('PRAGMA table_info(movies_movie)')
    for row in cur.fetchall():
        print('  ' + str(row))

print()
print('DETALLE movies_rating (FK a pelicula)')
print('-' * 60)
with connection.cursor() as cur:
    cur.execute('PRAGMA table_info(movies_rating)')
    for row in cur.fetchall():
        print('  ' + str(row))

print()
print('TABLA INTERMEDIA M2M movies_movie_generos')
print('-' * 60)
with connection.cursor() as cur:
    cur.execute("SELECT sql FROM sqlite_master WHERE name='movies_movie_generos'")
    print('  ' + cur.fetchone()[0])
