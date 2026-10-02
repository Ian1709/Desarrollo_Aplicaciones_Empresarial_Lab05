"""Pruebas de la app `movies`: modelos, panel y vista pública de recomendación."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Genre, Movie, Person, Rating

User = get_user_model()


class MovieModelTests(TestCase):
    def setUp(self):
        self.accion = Genre.objects.create(nombre='Acción')
        self.ficcion = Genre.objects.create(nombre='Ficción')
        self.nolan = Person.objects.create(nombre='Christopher', apellidos='Nolan')
        self.pelicula = Movie.objects.create(titulo='Inception', anio=2010)
        self.pelicula.generos.set([self.accion, self.ficcion])
        self.pelicula.directores.set([self.nolan])

    def test_str_de_los_cuatro_modelos(self):
        valoracion = Rating.objects.create(
            pelicula=self.pelicula, critico='Ana Ruiz', puntuacion=9
        )
        self.assertEqual(str(self.accion), 'Acción')
        self.assertEqual(str(self.nolan), 'Christopher Nolan')
        self.assertEqual(str(self.pelicula), 'Inception (2010)')
        self.assertEqual(str(valoracion), 'Inception - Ana Ruiz: 9/10')

    def test_relacion_muchos_a_muchos_con_generos(self):
        self.assertEqual(self.pelicula.generos.count(), 2)
        self.assertIn(self.pelicula, self.accion.peliculas.all())

    def test_relacion_uno_a_muchos_con_valoraciones(self):
        Rating.objects.create(pelicula=self.pelicula, critico='Ana Ruiz', puntuacion=9)
        Rating.objects.create(pelicula=self.pelicula, critico='Luis Fernández', puntuacion=7)
        self.assertEqual(self.pelicula.valoraciones.count(), 2)
        self.assertEqual(self.pelicula.valoracion_media, 8.0)

    def test_borrar_pelicula_borra_sus_valoraciones(self):
        Rating.objects.create(pelicula=self.pelicula, critico='Ana Ruiz', puntuacion=9)
        self.pelicula.delete()
        self.assertEqual(Rating.objects.count(), 0)


class AdminPanelTests(TestCase):
    def setUp(self):
        User.objects.create_superuser('admin', 'admin@lab05.local', 'admin123')
        User.objects.create_user('editor', password='editor123', is_staff=True)
        self.cliente = self.client
        self.cliente.login(username='admin', password='admin123')
        self.genero = Genre.objects.create(nombre='Drama')
        self.pelicula = Movie.objects.create(titulo='Gravity', anio=2013)
        self.pelicula.generos.set([self.genero])

    def test_cuatro_modelos_registrados_en_el_panel(self):
        from django.contrib import admin as dj_admin

        for modelo in (Movie, Genre, Person, Rating):
            self.assertIn(modelo, dj_admin.site._registry)

    def test_listado_y_alta_de_los_cuatro_modelos(self):
        for slug in ('movie', 'genre', 'person', 'rating'):
            with self.subTest(modelo=slug):
                self.assertEqual(self.cliente.get(f'/admin/movies/{slug}/').status_code, 200)
                self.assertEqual(self.cliente.get(f'/admin/movies/{slug}/add/').status_code, 200)

    def test_inline_de_valoraciones_en_el_formulario(self):
        respuesta = self.cliente.get(f'/admin/movies/movie/{self.pelicula.pk}/change/')
        self.assertEqual(respuesta.status_code, 200)
        formset = respuesta.context['inline_admin_formsets'][0].formset
        self.assertIn('critico', formset.forms[0].fields)
        self.assertIn('puntuacion', formset.forms[0].fields)

    def test_campos_de_auditoria_en_solo_lectura(self):
        respuesta = self.cliente.get(f'/admin/movies/movie/{self.pelicula.pk}/change/')
        campos = respuesta.context['adminform'].form.fields
        self.assertNotIn('fecha_creacion', campos)
        self.assertNotIn('fecha_modificacion', campos)

    def test_alta_de_pelicula_con_valoraciones_desde_el_panel(self):
        respuesta = self.cliente.post(
            '/admin/movies/movie/add/',
            {
                'titulo': 'Dune',
                'anio': 2021,
                'sinopsis': 'Un feudero en el desierto.',
                'generos': [self.genero.pk],
                'valoraciones-TOTAL_FORMS': '1',
                'valoraciones-INITIAL_FORMS': '0',
                'valoraciones-MIN_NUM_FORMS': '0',
                'valoraciones-MAX_NUM_FORMS': '1000',
                'valoraciones-0-critico': 'Ana Ruiz',
                'valoraciones-0-puntuacion': '8',
                'valoraciones-0-comentario': 'Impresionante.',
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        pelicula = Movie.objects.get(titulo='Dune')
        self.assertEqual(pelicula.valoraciones.count(), 1)
        self.assertEqual(pelicula.valoraciones.first().puntuacion, 8)

    def test_busqueda_y_filtros_del_listado(self):
        Movie.objects.create(titulo='Interest', anio=1995)
        respuesta = self.cliente.get('/admin/movies/movie/', {'q': 'Interest'})
        self.assertEqual(respuesta.context['cl'].result_count, 1)
        respuesta = self.cliente.get('/admin/movies/movie/', {'decada': '2010'})
        self.assertEqual(respuesta.context['cl'].result_count, 1)
        respuesta = self.cliente.get(
            '/admin/movies/movie/', {'generos__id__exact': self.genero.pk}
        )
        self.assertEqual(respuesta.context['cl'].result_count, 1)


class EditorPermisosTests(TestCase):
    """Paso 9: el grupo "editores" puede añadir y cambiar, pero no eliminar."""

    def setUp(self):
        self.superusuario = User.objects.create_superuser(
            'admin', 'admin@lab05.local', 'admin123'
        )
        from django.contrib.auth.models import Group, Permission

        self.grupo = Group.objects.create(name='editores')
        self.grupo.permissions.set(
            Permission.objects.filter(
                content_type__app_label='movies',
                codename__in=['add_movie', 'change_movie', 'view_movie'],
            )
        )
        self.editor = User.objects.create_user(
            'editor', password='editor123', is_staff=True
        )
        self.editor.groups.add(self.grupo)
        self.pelicula = Movie.objects.create(titulo='Gravity', anio=2013)

    def test_el_editor_no_tiene_permiso_de_borrado(self):
        self.assertFalse(self.editor.has_perm('movies.delete_movie'))
        self.assertTrue(self.editor.has_perm('movies.add_movie'))
        self.assertTrue(self.editor.has_perm('movies.change_movie'))

    def test_el_editor_ve_las_peliculas_pero_no_puede_borrarlas(self):
        self.client.login(username='editor', password='editor123')
        self.assertEqual(self.client.get('/admin/movies/movie/').status_code, 200)
        self.assertEqual(self.client.get('/admin/movies/movie/add/').status_code, 200)
        self.assertEqual(
            self.client.get(f'/admin/movies/movie/{self.pelicula.pk}/change/').status_code, 200
        )
        self.assertEqual(
            self.client.get(f'/admin/movies/movie/{self.pelicula.pk}/delete/').status_code, 403
        )
        self.assertNotIn('delete_selected', self.client.get('/admin/movies/movie/').content.decode())

    def test_el_editor_no_ve_los_otros_tres_modelos(self):
        self.client.login(username='editor', password='editor123')
        for slug in ('genre', 'person', 'rating'):
            with self.subTest(modelo=slug):
                self.assertEqual(self.client.get(f'/admin/movies/{slug}/').status_code, 403)

    def test_el_superusuario_si_puede_borrar(self):
        self.client.login(username='admin', password='admin123')
        self.assertEqual(
            self.client.get(f'/admin/movies/movie/{self.pelicula.pk}/delete/').status_code, 200
        )


class RecomendacionViewTests(TestCase):
    """Paso 10: la vista pública de recomendación."""

    def setUp(self):
        self.drama = Genre.objects.create(nombre='Drama')
        self.ciencia = Genre.objects.create(nombre='Ciencia ficción')
        self.nolan = Person.objects.create(nombre='Christopher', apellidos='Nolan')
        self.inception = self.crear('Inception', 2010, [self.ciencia], 9)
        self.interest = self.crear('Interest', 1995, [self.ciencia], 8)
        self.gravity = self.crear('Gravity', 2013, [self.ciencia, self.drama], 7)
        self.sindler = self.crear('La lista de Schindler', 1993, [self.drama], 10)
        self.sin_generos = Movie.objects.create(titulo='Sin géneros', anio=2020)

    def crear(self, titulo, anio, generos, puntuacion):
        pelicula = Movie.objects.create(titulo=titulo, anio=anio, duracion=120)
        pelicula.generos.set(generos)
        pelicula.directores.set([self.nolan])
        Rating.objects.create(
            pelicula=pelicula, critico='Crítico de prueba', puntuacion=puntuacion
        )
        return pelicula

    def test_el_listado_muestra_las_peliculas_ordenadas_por_valoracion(self):
        respuesta = self.client.get(reverse('movies:movie_list'))
        self.assertEqual(respuesta.status_code, 200)
        titulos = [p.titulo for p in respuesta.context['peliculas']]
        self.assertEqual(titulos[0], 'La lista de Schindler')
        self.assertIn('Inception', titulos)

    def test_recomienda_peliculas_del_mismo_genero_mejor_valoradas(self):
        respuesta = self.client.get(
            reverse('movies:movie_detail', args=[self.inception.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        recomendados = [p.titulo for p in respuesta.context['recomendaciones']]
        self.assertIn('Interest', recomendados)
        self.assertIn('Gravity', recomendados)
        self.assertNotIn('Inception', recomendados)  # se excluye ella misma
        self.assertNotIn('La lista de Schindler', recomendados)  # no comparte género
        self.assertEqual(recomendados[0], 'Interest')  # la mejor valorada del mismo género

    def test_una_pelicula_sin_generos_no_recomienda_nada(self):
        respuesta = self.client.get(
            reverse('movies:movie_detail', args=[self.sin_generos.pk])
        )
        self.assertEqual(list(respuesta.context['recomendaciones']), [])

    def test_mejores_por_genero(self):
        respuesta = self.client.get(reverse('movies:movie_list'))
        generos = [g.nombre for g, _ in respuesta.context['mejores_por_genero']]
        self.assertEqual(generos, ['Ciencia ficción', 'Drama'])  # Meta.ordering = ['nombre']

    def test_pelicula_inexistente_devuelve_404(self):
        self.assertEqual(
            self.client.get(reverse('movies:movie_detail', args=[9999])).status_code, 404
        )