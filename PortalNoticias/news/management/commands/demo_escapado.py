"""Paso 12: guarda una noticia con etiquetas HTML en el cuerpo y muestra qué
pinta el portal y por qué.

    python manage.py demo_escapado

Crea (o reutiliza) una categoría, un autor y una noticia cuyo cuerpo contiene
HTML, pide la página de detalle con el cliente de pruebas y muestra el fragmento
de HTML que Django devuelve.
"""

import re

from django.core.management.base import BaseCommand
from django.test import Client

from news.models import Article, Author, Category

CUERPO = (
    'Este párrafo lo escribió el redactor con una etiqueta '
    '<b>en negrita</b> y un aviso <script>alert("xss")</script> dentro del texto.'
)

RESUMEN = 'Resumen con <b>negrita</b> y <i>cursiva</i> escritas a mano.'


class Command(BaseCommand):
    help = 'Demuestra el escapado automático de plantillas con una noticia que contiene HTML.'

    def handle(self, *args, **options):
        categoria, _ = Category.objects.get_or_create(name='Tecnología')
        autor, _ = Author.objects.get_or_create(name='Equipo de redacción')

        articulo, _ = Article.objects.get_or_create(
            title='Prueba de escapado automático',
            defaults={'summary': RESUMEN, 'body': CUERPO, 'author': autor},
        )
        articulo.summary = RESUMEN
        articulo.body = CUERPO
        articulo.save()
        articulo.categories.add(categoria)

        cliente = Client()
        respuesta = cliente.get(f'/noticia/{articulo.pk}/')
        html = respuesta.content.decode()

        self.stdout.write(f'Noticia guardada con id={articulo.pk} (HTTP {respuesta.status_code})')
        self.stdout.write('')
        self.stdout.write('Cuerpo guardado en la base de datos:')
        self.stdout.write(f'  {CUERPO}')
        self.stdout.write('')
        self.stdout.write('HTML que devuelve la página de detalle:')

        bloque = re.search(r'<div class="noticia-cuerpo">(.*?)</div>', html, re.S)
        if bloque:
            self.stdout.write(bloque.group(0).strip())

        self.stdout.write('')
        self.stdout.write('El resumen en la portada:')
        portada = cliente.get('/').content.decode()
        trozo = re.search(r'<p class="tarjeta-resumen">(.*?)</p>', portada, re.S)
        if trozo:
            self.stdout.write(trozo.group(0).strip())

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            'El navegador NO ejecuta el <script>: la plantilla muestra el texto '
            'escapado (&lt;script&gt;...) porque el autoescapado de Django está activo.'
        ))
