"""Paso 9: crea el grupo "editores" y un usuario dentro de ese grupo.

El grupo puede AÑADIR y CAMBIAR películas, pero NO puede eliminarlas: por eso no se
le asigna el permiso movies.delete_movie. Se le asigna además view_movie porque
Django exige permiso de lectura para llegar a las pantallas de listado y de alta.

    python manage.py crear_grupo_editores
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Permisos del grupo: añadir y cambiar (nunca eliminar)
PERMISOS = ['add_movie', 'change_movie', 'view_movie']
PERMISO_PROHIBIDO = 'delete_movie'


class Command(BaseCommand):
    help = 'Crea el grupo "editores" (sin permiso de borrado) y el usuario "editor".'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='editor')
        parser.add_argument('--password', default='editor123')
        parser.add_argument('--email', default='editor@lab05.local')

    def handle(self, *args, **options):
        User = get_user_model()

        grupo, _ = Group.objects.get_or_create(name='editores')
        permisos = list(
            Permission.objects.filter(
                content_type__app_label='movies', codename__in=PERMISOS
            )
        )
        grupo.permissions.set(permisos)
        self.stdout.write(f'Grupo "editores" con {len(permisos)} permiso(s):')
        for permiso in permisos:
            self.stdout.write(f'  - {permiso.content_type.model}.{permiso.codename} ({permiso.name})')

        prohibido = Permission.objects.filter(
            content_type__app_label='movies', codename=PERMISO_PROHIBIDO
        ).first()
        tiene_borrado = grupo.permissions.filter(pk=prohibido.pk).exists() if prohibido else False
        self.stdout.write(
            f'  - {PERMISO_PROHIBIDO} asignado: {tiene_borrado} '
            '(False = el editor NO puede eliminar películas)'
        )

        usuario, creado = User.objects.get_or_create(
            username=options['username'],
            defaults={'email': options['email']},
        )
        usuario.is_staff = True
        usuario.is_superuser = False
        usuario.set_password(options['password'])
        usuario.save()
        usuario.groups.add(grupo)

        self.stdout.write('')
        self.stdout.write(
            f'Usuario "{usuario.username}" '
            f'({"creado" if creado else "actualizado"}): is_staff={usuario.is_staff} '
            f'is_superuser={usuario.is_superuser} grupos={list(usuario.groups.values_list("name", flat=True))}'
        )
        self.stdout.write(f'  contraseña: {options["password"]}')
        self.stdout.write('')
        self.stdout.write('Permisos efectivos del usuario dentro del panel:')
        for permiso in sorted(usuario.get_all_permissions()):
            self.stdout.write(f'  {permiso}')