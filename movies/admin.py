from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Avg

from .models import Genre, Movie, Person, Rating


class FiltroAnio(SimpleListFilter):
    """Filtro por año (décadas) declarado en `MovieAdmin.list_filter` (Paso 5)."""

    title = 'década de estreno'
    parameter_name = 'decada'

    def lookups(self, request, model_admin):
        return (
            ('2020', '2020 - 2029'),
            ('2010', '2010 - 2019'),
            ('2000', '2000 - 2009'),
            ('1990', '1990 - 1999'),
            ('anteriores', '1988 - 1999'),
        )

    def queryset(self, request, queryset):
        valor = self.value()
        if not valor:
            return queryset
        if valor == 'anteriores':
            return queryset.filter(anio__lt=2000)
        return queryset.filter(anio__gte=int(valor), anio__lte=int(valor) + 9)


class RatingInline(admin.TabularInline):
    """Paso 6: bloque de líneas con las valoraciones dentro del formulario de la película.

    Permite darlas de alta y editarlas sin salir del registro de la película
    (una película, varias valoraciones: FK `Rating.pelicula`).
    """

    model = Rating
    extra = 1
    fields = ('critico', 'puntuacion', 'comentario')
    ordering = ('-puntuacion',)
    verbose_name = 'valoración'
    verbose_name_plural = 'valoraciones (alta y edición en la misma pantalla)'
    show_change_link = True


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Columnas útiles, filtro por género y por año, y búsqueda por título y nombre."""

    inlines = [RatingInline]
    list_display = (
        'titulo',
        'anio',
        'generos_texto',
        'directores_texto',
        'num_valoraciones',
        'valoracion_media',
    )
    list_filter = ('generos', FiltroAnio)
    search_fields = ('titulo', 'directores__nombre', 'directores__apellidos')
    filter_horizontal = ('generos', 'directores')
    ordering = ('-anio', 'titulo')
    list_per_page = 25

    # Paso 7: los campos de auditoría se muestran pero no se pueden editar
    # (los gestiona Django con auto_now_add / auto_now).
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')

    @admin.display(description='géneros', ordering='generos__nombre')
    def generos_texto(self, obj):
        return ', '.join(g.nombre for g in obj.generos.all())

    @admin.display(description='directores', ordering='directores__apellidos')
    def directores_texto(self, obj):
        return ', '.join(str(p) for p in obj.directores.all())

    @admin.display(description='valoraciones')
    def num_valoraciones(self, obj):
        return obj.valoraciones.count()

    @admin.display(description='valoración media', ordering='media')
    def valoracion_media(self, obj):
        media = getattr(obj, 'media', None)
        return f'{media:.2f}' if media is not None else '—'

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(media=Avg('valoraciones__puntuacion'))
            .distinct()
        )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'num_peliculas')
    search_fields = ('nombre',)
    ordering = ('nombre',)

    @admin.display(description='nº de películas')
    def num_peliculas(self, obj):
        return obj.peliculas.count()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'pais', 'fecha_nacimiento', 'num_peliculas')
    list_filter = ('pais',)
    search_fields = ('nombre', 'apellidos')
    ordering = ('apellidos', 'nombre')

    @admin.display(description='nº de películas')
    def num_peliculas(self, obj):
        return obj.peliculas_dirigidas.count()


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'critico', 'puntuacion', 'fecha_creacion')
    list_filter = ('puntuacion', 'fecha_creacion')
    search_fields = ('critico', 'pelicula__titulo')
    ordering = ('-puntuacion',)
    autocomplete_fields = ('pelicula',)
