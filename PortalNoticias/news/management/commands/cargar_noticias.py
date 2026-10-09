"""Carga noticias de ejemplo en el portal.

    python manage.py cargar_noticias            # añade lo que falte
    python manage.py cargar_noticias --reset    # borra todo y vuelve a crear

Genera las imágenes destacadas y las fotos de los autores con Pillow, y deja
seis noticias repartidas en tres categorías (dos por categoría).
"""

from datetime import timedelta
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw

from news.models import Article, Author, Category

CATEGORIAS = [
    ('Política', 'Actualidad política nacional e internacional.'),
    ('Deportes', 'Resultados, fichajes y competiciones.'),
    ('Cultura', 'Cine, música, literatura y arte.'),
]

AUTORES = [
    ('Ana Beltrán', 'ana.beltran@portal.test', 'Redactora de política.'),
    ('Diego Salazar', 'diego.salazar@portal.test', 'Redactor de deportes y cultura.'),
]

NOTICIAS = [
    # (categoría, autor, título, resumen, cuerpo, color)
    ('Política', 'Ana Beltrán', 'El Congreso aprueba la reforma del sistema de pensiones',
     'La norma sale adelante con 176 votos a favor y entra en vigor el próximo trimestre.',
     'Tras un pleno de casi seis horas, el Congreso aprobó la reforma del sistema de '
     'pensiones con 176 votos a favor. La norma actualiza el cálculo de la jubilación y '
     'entra en vigor el próximo trimestre.',
     (192, 57, 43)),
    ('Política', 'Ana Beltrán', 'Los gobiernos regionales pactan un fondo común de inversión',
     'Seis comunidades acuerdan compartir proyectos de infraestructura por cinco años.',
     'Seis comunidades autónomas firmaron un acuerdo para crear un fondo común de '
     'inversión en infraestructura durante los próximos cinco años.',
     (142, 68, 173)),
    ('Deportes', 'Diego Salazar', 'La selección femenina se clasifica para la final continental',
     'Gol en el minuto 89 y una actuación impecable de la portera sella el pase.',
     'La selección femenina jugará la final continental después de ganar 1-0 con un gol '
     'en el minuto 89 y una actuación impecable de su portera.',
     (39, 174, 96)),
    ('Deportes', 'Diego Salazar', 'El maratón de la ciudad bate su récord de participantes',
     'Más de 42.000 corredores tomarán la salida el próximo domingo.',
     'La organización confirmó que 42.100 corredores tomarán la salida el próximo domingo, '
     'la cifra más alta en la historia del maratón.',
     (41, 128, 185)),
    ('Cultura', 'Diego Salazar', 'El festival de cine abre con una retrospectiva del cine mudo',
     'La muestra recupera veinte películas restauradas de los años veinte.',
     'El festival de cine arrancó anoche con una retrospectiva que recupera veinte '
     'películas mudas restauradas, acompañadas por música en directo.',
     (211, 84, 0)),
    ('Cultura', 'Ana Beltrán', 'Una novela sobre la memoria gana el premio de narrativa',
     'El jurado destaca su "construcción de personajes y su mirada sobre el pasado".',
     'La novela premiada, centrada en la memoria familiar, recibió el galardón por '
     'unanimidad del jurado, que destacó su construcción de personajes.',
     (243, 156, 18)),
]


def imagen(texto, color, ancho=800, alto=450):
    """Genera una imagen destacada en memoria (sin depender de archivos externos)."""
    im = Image.new('RGB', (ancho, alto), color)
    dibujo = ImageDraw.Draw(im)
    dibujo.rectangle([20, 20, ancho - 20, alto - 20], outline=(255, 255, 255), width=4)
    dibujo.text((50, alto // 2 - 10), texto, fill=(255, 255, 255))
    buffer = BytesIO()
    im.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Carga categorías, autores y seis noticias de ejemplo en el portal.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Borra los datos existentes antes de cargar.')

    def handle(self, *args, **options):
        if options['reset']:
            Article.objects.all().delete()
            Author.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write('Datos anteriores eliminados.')

        categorias = {}
        for nombre, descripcion in CATEGORIAS:
            categoria, _ = Category.objects.get_or_create(
                name=nombre, defaults={'description': descripcion}
            )
            categorias[nombre] = categoria

        autores = {}
        for nombre, email, bio in AUTORES:
            autor, creado = Author.objects.get_or_create(
                name=nombre, defaults={'email': email, 'bio': bio}
            )
            if creado:
                autor.photo.save(
                    f'{autor.slug}.png', imagen(nombre, (52, 73, 94), 300, 300), save=True
                )
            autores[nombre] = autor

        creadas = 0
        ahora = timezone.now()
        for indice, (cat, autor, titulo, resumen, cuerpo, color) in enumerate(NOTICIAS):
            articulo, creado = Article.objects.get_or_create(
                title=titulo,
                defaults={
                    'summary': resumen,
                    'body': cuerpo,
                    'author': autores[autor],
                    'published_at': ahora - timedelta(days=indice),
                },
            )
            if creado:
                articulo.categories.add(categorias[cat])
                articulo.featured_image.save(
                    f'noticia-{indice + 1}.png', imagen(titulo, color), save=True
                )
                creadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Categorías: {Category.objects.count()} | '
            f'Autores: {Author.objects.count()} | '
            f'Noticias: {Article.objects.count()} (nuevas: {creadas})'
        ))
