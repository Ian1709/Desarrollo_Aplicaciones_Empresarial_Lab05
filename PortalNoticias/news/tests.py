"""Casos de prueba del portal de noticias.

Se ejecutan con:  python manage.py test news
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category

User = get_user_model()


class ModelosTests(TestCase):
    def setUp(self):
        self.categoria = Category.objects.create(name='Deportes')
        self.autor = Author.objects.create(name='Diego Salazar', email='diego@portal.test')
        self.noticia = Article.objects.create(
            title='La selección gana la final',
            summary='Resumen de prueba',
            body='Cuerpo de prueba',
            author=self.autor,
        )
        self.noticia.categories.add(self.categoria)

    def test_str_de_los_tres_modelos(self):
        self.assertEqual(str(self.categoria), 'Deportes')
        self.assertEqual(str(self.autor), 'Diego Salazar')
        self.assertEqual(str(self.noticia), 'La selección gana la final')

    def test_los_slug_se_generan_solos(self):
        self.assertEqual(self.categoria.slug, 'deportes')
        self.assertEqual(self.autor.slug, 'diego-salazar')
        self.assertEqual(self.noticia.slug, 'la-seleccion-gana-la-final')

    def test_relacion_muchos_a_muchos_con_categorias(self):
        otra = Category.objects.create(name='Cultura')
        self.noticia.categories.add(otra)
        self.assertEqual(self.noticia.categories.count(), 2)
        self.assertIn(self.noticia, self.categoria.articles.all())

    def test_orden_por_fecha_de_publicacion_descendente(self):
        reciente = Article.objects.create(
            title='Más reciente', summary='x', body='y', author=self.autor,
            published_at=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(Article.objects.first(), reciente)

    def test_no_se_puede_borrar_un_autor_con_noticias(self):
        from django.db.models.deletion import ProtectedError

        with self.assertRaises(ProtectedError):
            self.autor.delete()

    def test_get_absolute_url_apunta_al_detalle(self):
        self.assertEqual(
            self.noticia.get_absolute_url(),
            reverse('news:article_detail', args=[self.noticia.pk]),
        )


class VistasTests(TestCase):
    def setUp(self):
        self.categoria = Category.objects.create(name='Cultura')
        self.autor = Author.objects.create(name='Ana Beltrán')
        self.noticia = Article.objects.create(
            title='Una novela gana el premio',
            summary='Resumen de la noticia',
            body='Cuerpo de la noticia',
            author=self.autor,
        )
        self.noticia.categories.add(self.categoria)

    def test_la_portada_responde_y_muestra_la_noticia(self):
        respuesta = self.client.get(reverse('news:index'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Una novela gana el premio')
        self.assertContains(respuesta, 'class="tarjeta"')

    def test_el_detalle_muestra_autor_y_categorias(self):
        respuesta = self.client.get(reverse('news:article_detail', args=[self.noticia.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ana Beltrán')
        self.assertContains(respuesta, 'Cultura')

    def test_el_listado_por_categoria_reutiliza_la_tarjeta(self):
        respuesta = self.client.get(reverse('news:category_list', args=[self.categoria.slug]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'class="tarjeta"')
        self.assertContains(respuesta, self.noticia.title)

    def test_una_categoria_inexistente_devuelve_404(self):
        self.assertEqual(self.client.get('/categoria/no-existe/').status_code, 404)

    def test_una_noticia_inexistente_devuelve_404(self):
        self.assertEqual(self.client.get('/noticia/9999/').status_code, 404)

    def test_los_enlaces_se_construyen_con_url(self):
        respuesta = self.client.get(reverse('news:index'))
        self.assertContains(respuesta, reverse('news:article_detail', args=[self.noticia.pk]))
        self.assertContains(respuesta, reverse('news:category_list', args=[self.categoria.slug]))


class EscapadoAutomaticoTests(TestCase):
    """Paso 12: Django escapa por defecto lo que viene de la base de datos."""

    def setUp(self):
        self.categoria = Category.objects.create(name='Tecnología')
        self.autor = Author.objects.create(name='Autor de pruebas')
        self.noticia = Article.objects.create(
            title='Prueba <b>de</b> escapado',
            summary='Resumen con <b>negrita</b>',
            body='Texto normal <script>alert("xss")</script> y <b>negrita</b> final.',
            author=self.autor,
        )
        self.noticia.categories.add(self.categoria)

    def test_el_cuerpo_se_muestra_escapado(self):
        respuesta = self.client.get(reverse('news:article_detail', args=[self.noticia.pk]))
        contenido = respuesta.content.decode()
        self.assertIn('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;', contenido)
        self.assertNotIn('<script>alert("xss")</script>', contenido)

    def test_el_titulo_se_muestra_escapado(self):
        respuesta = self.client.get(reverse('news:index'))
        contenido = respuesta.content.decode()
        self.assertIn('Prueba &lt;b&gt;de&lt;/b&gt; escapado', contenido)
        self.assertNotIn('<b>de</b>', contenido)

    def test_la_etiqueta_no_se_interpreta_salvo_que_se_marque_como_segura(self):
        self.noticia.body = '<b>negrita</b>'
        respuesta = self.client.get(reverse('news:article_detail', args=[self.noticia.pk]))
        self.assertNotIn('<b>negrita</b>', respuesta.content.decode())


class AdminTests(TestCase):
    def setUp(self):
        User.objects.create_superuser('admin', 'admin@portal.test', 'admin123')
        self.client.login(username='admin', password='admin123')

    def test_los_tres_modelos_estan_registrados(self):
        for slug in ('category', 'author', 'article'):
            with self.subTest(modelo=slug):
                self.assertEqual(self.client.get(f'/admin/news/{slug}/').status_code, 200)
                self.assertEqual(self.client.get(f'/admin/news/{slug}/add/').status_code, 200)

    def test_el_listado_de_noticias_tiene_filtros_y_buscador(self):
        respuesta = self.client.get('/admin/news/article/')
        self.assertContains(respuesta, 'id="searchbar"')
        self.assertContains(respuesta, 'changelist-filter')
