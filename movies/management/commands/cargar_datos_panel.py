"""Paso 8: carga de datos de prueba escribiendo en los formularios del panel.

En lugar de insertar filas con el ORM, este comando reproduce lo que hace una
persona delante del navegador: se autentica en /admin/ y envía un POST a los
formularios de alta de generos, personas y peliculas, incluyendo el bloque de
lineas de las valoraciones (Paso 6) y un cartel generado con Pillow (Paso 1).

    python manage.py cargar_datos_panel
    python manage.py cargar_datos_panel --reset
"""

import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.test import Client
from django.test.utils import setup_test_environment
from PIL import Image, ImageDraw

from movies.models import Genre, Movie, Person, Rating

PREFIX_INLINE = 'valoraciones'

GENEROS = [
    ('Drama', 'Dramas sobre conflictos humanos y sociales'),
    ('Misterio', 'Suspense, enigmas y acertijos'),
    ('Ciencia ficción', 'Ficción especulativa y mundos futuristas'),
    ('Aventura', 'Exploración, riesgo y viajes extraordinarios'),
]

PERSONAS = [
    ('Christopher', 'Nolan', '1970-07-30', 'Reino Unido'),
    ('Stanley', 'Kubrick', '1928-10-26', 'Estados Unidos'),
    ('Quentin', 'Tarantino', '1963-03-27', 'Estados Unidos'),
    ('Steven', 'Spielberg', '1946-12-18', 'Estados Unidos'),
    ('Alfonso', 'Cuarón', '1961-11-28', 'México'),
]

# Entry structure: titulo, anio, duracion, sinopsis, generos, director, valoraciones
# Each rating: (critico, puntuacion, comentario)
PELICULAS = [
    (
        'Inception',
        2010,
        148,
        'Un ladrón que roba secretos dentro de los sueños descubre que debe '
        'retroceder en el tiempo para corregir su propia vida.',
        ['Ciencia ficción', 'Misterio'],
        'Christopher Nolan',
        [
            ('Ana Ruiz', 9, 'Estructura de relojería y una idea brillante.'),
            ('Luis Fernández', 8, 'Se entiende de más, pero el final es redondo.'),
        ],
        True,
    ),
    (
        'Interest',
        1995,
        130,
        'Un agente del FBI investiga los asesinatos encontrados en una página de prensa.',
        ['Misterio'],
        'Christopher Nolan',
        [
            ('María Gómez', 9, 'La mejor película policial de la década.'),
            ('Carlos Pérez', 8, 'Vigente después de treinta años.'),
            ('Sofía Díaz', 7, 'El final sigue siendo discutible.'),
        ],
        False,
    ),
    (
        '2001: Una odisea espacial',
        1968,
        149,
        'La humanidad controla una inteligencia artificial que decide sobre su futuro.',
        ['Ciencia ficción'],
        'Stanley Kubrick',
        [
            ('Jorge Martín', 9, 'La banda sonora marca época.'),
        ],
        False,
    ),
    (
        'El resplandor',
        1980,
        146,
        'Un escritor se convierte en guardián de un hotel aislado junto a su familia.',
        ['Misterio', 'Drama'],
        'Stanley Kubrick',
        [
            ('Elena Vega', 8, 'La ambientación es lo mejor de la película.'),
        ],
        False,
    ),
    (
        'Pulp Fiction',
        1994,
        154,
        'Varias historias del bajo mundo de Los Angeles se entrelazan de forma no lineal.',
        ['Misterio', 'Drama'],
        'Quentin Tarantino',
        [
            ('David Ortiz', 10, 'Guion y diálogos impecables.'),
            ('Carmen Nieto', 9, 'Una obra maestra del cine independiente.'),
        ],
        False,
    ),
    (
        'Django: Unidos por el rencor',
        2012,
        165,
        'Un esclavo liberado busca a su esposa en el Mississippi del siglo XIX.',
        ['Drama', 'Aventura'],
        'Quentin Tarantino',
        [],
        False,
    ),
    (
        'La lista de Schindler',
        1993,
        195,
        'Un empresario alemán salva de la muerte a más de mil judíos.',
        ['Drama'],
        'Steven Spielberg',
        [
            ('Pablo Lara', 10, 'La película más emotiva del siglo XXI.'),
        ],
        False,
    ),
    (
        'E.T. el extraterrestre',
        1982,
        115,
        'Un niño conoce a una criatura extraterrestre que quiere volver a casa.',
        ['Ciencia ficción', 'Aventura'],
        'Steven Spielberg',
        [],
        False,
    ),
    (
        'Parque Jurásico',
        1993,
        127,
        'Un parque temático con dinosaurios creados se abre al público.',
        ['Aventura'],
        'Steven Spielberg',
        [],
        False,
    ),
    (
        'Gravity',
        2013,
        91,
        'Dos astrónautas permanecen varados en órbita tras la destrucción de su nave.',
        ['Ciencia ficción', 'Drama'],
        'Alfonso Cuarón',
        [
            ('Lucía Ramos', 7, 'Espectacular, aunque algo predecible.'),
            ('Andrés Gil', 8, 'La coreografía de la órbita es espectacular.'),
        ],
        False,
    ),
]


def cartel_de_prueba(titulo):
    """Genera un cartel JPEG con Pillow (justifica la instalación de Pillow)."""
    imagen = Image.new('RGB', (300, 450), (24, 28, 46))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle([20, 20, 280, 430], outline=(220, 200, 120), width=4)
    dibujo.text((35, 200), titulo[:28], fill=(240, 240, 240))
    buffer = io.BytesIO()
    imagen.save(buffer, format='JPEG')
    nombre = titulo.lower().replace(' ', '_').replace(':', '')
    return SimpleUploadedFile(
        f'{nombre}.jpg', buffer.getvalue(), content_type='image/jpeg'
    )


class Command(BaseCommand):
    help = (
        'Carga 4 generos, 5 personas, 10 peliculas y sus valoraciones usando los '
        'formularios del panel de administracion (POST a /admin/).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Borra los datos de prueba existentes antes de cargar.',
        )

    def handle(self, *args, **options):
        setup_test_environment()

        User = get_user_model()
        superusuario = User.objects.filter(is_superuser=True).order_by('id').first()
        if superusuario is None:
            self.stderr.write('No hay superusuario: crea uno con manage.py createsuperuser')
            return

        if options['reset']:
            Rating.objects.all().delete()
            Movie.objects.all().delete()
            Person.objects.all().delete()
            Genre.objects.all().delete()
            self.stdout.write('Datos anteriores eliminados (--reset)')

        cliente = Client()
        cliente.force_login(superusuario)
        self.stdout.write(f'Sesión iniciada en /admin/ como "{superusuario.username}"')

        # --- Géneros ---------------------------------------------------------
        for nombre, descripcion in GENEROS:
            if Genre.objects.filter(nombre=nombre).exists():
                continue
            respuesta = cliente.post(
                '/admin/movies/genre/add/',
                {'nombre': nombre, 'descripcion': descripcion},
            )
            if respuesta.status_code != 302:
                self.stderr.write(f'ERROR al crear el género {nombre}: {respuesta.status_code}')
            else:
                self.stdout.write(f'  género creado desde el panel: {nombre}')

        # --- Personas --------------------------------------------------------
        for nombre, apellidos, nacimiento, pais in PERSONAS:
            if Person.objects.filter(nombre=nombre, apellidos=apellidos).exists():
                continue
            respuesta = cliente.post(
                '/admin/movies/person/add/',
                {
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'fecha_nacimiento': nacimiento,
                    'pais': pais,
                },
            )
            if respuesta.status_code != 302:
                self.stderr.write(f'ERROR al crear la persona {nombre}: {respuesta.status_code}')
            else:
                self.stdout.write(f'  persona creada desde el panel: {nombre} {apellidos}')

        # --- Películas con sus valoraciones (bloque de líneas del Paso 6) ---
        for (titulo, anio, duracion, sinopsis, generos, director, valoraciones, con_cartel) in PELICULAS:
            if Movie.objects.filter(titulo=titulo).exists():
                continue
            datos = {
                'titulo': titulo,
                'anio': anio,
                'duracion': duracion,
                'sinopsis': sinopsis,
                'generos': [g.pk for g in Genre.objects.filter(nombre__in=generos)],
                'directores': list(
                    Person.objects.filter(
                        nombre=director.split()[0], apellidos=director.split()[-1]
                    ).values_list('pk', flat=True)
                ),
                f'{PREFIX_INLINE}-TOTAL_FORMS': str(len(valoraciones)),
                f'{PREFIX_INLINE}-INITIAL_FORMS': '0',
                f'{PREFIX_INLINE}-MIN_NUM_FORMS': '0',
                f'{PREFIX_INLINE}-MAX_NUM_FORMS': '1000',
            }
            for indice, (critico, puntuacion, comentario) in enumerate(valoraciones):
                datos[f'{PREFIX_INLINE}-{indice}-critico'] = critico
                datos[f'{PREFIX_INLINE}-{indice}-puntuacion'] = str(puntuacion)
                datos[f'{PREFIX_INLINE}-{indice}-comentario'] = comentario
            if con_cartel:
                datos['cartel'] = cartel_de_prueba(titulo)

            respuesta = cliente.post('/admin/movies/movie/add/', datos)
            if respuesta.status_code != 302:
                self.stderr.write(f'ERROR al crear la película {titulo}: {respuesta.status_code}')
                if respuesta.context and 'adminform' in respuesta.context:
                    form = respuesta.context['adminform'].form
                    self.stderr.write(f'  errores del formulario: {form.errors}')
                continue
            detalle = f'{len(valoraciones)} valoración(es)' if valoraciones else 'sin valoraciones'
            self.stdout.write(f'  película creada desde el panel: {titulo} ({anio}) - {detalle}')

        # --- Resumen ---------------------------------------------------------
        peliculas_con_valoracion = Movie.objects.filter(valoraciones__isnull=False).distinct().count()
        self.stdout.write('')
        self.stdout.write('RESUMEN DE LA CARGA (Paso 8)')
        self.stdout.write('-' * 60)
        self.stdout.write(f'  Géneros: {Genre.objects.count()}')
        self.stdout.write(f'  Personas: {Person.objects.count()}')
        self.stdout.write(f'  Películas: {Movie.objects.count()}')
        self.stdout.write(f'  Valoraciones: {Rating.objects.count()}')
        self.stdout.write(f'  Películas con al menos una valoración: {peliculas_con_valoracion}')
        self.stdout.write('-' * 60)
        for pelicula in Movie.objects.prefetch_related('generos', 'valoraciones'):
            generos = ', '.join(g.nombre for g in pelicula.generos.all())
            puntuaciones = [str(v.puntuacion) for v in pelicula.valoraciones.all()]
            media = f'{pelicula.valoracion_media:.2f}' if pelicula.valoracion_media else '—'
            self.stdout.write(
                f'  {pelicula.titulo} ({pelicula.anio}) | géneros: {generos} | '
                f'valoraciones: {puntuaciones or "ninguna"} | media: {media}'
            )
        self.stdout.write('')
        self.stdout.write('Los datos se han escrito con los formularios del panel (/admin/).')