"""Modelos de la app `movies` — Lab05 (Desarrollo de Aplicaciones Empresariales).

Relaciones del enunciado:
- Movie <-> Genre  : muchos a muchos (`Movie.generos`)
- Movie -> Rating  : clave foránea (`Rating.pelicula`, una película, varias valoraciones)
- Movie <-> Person : muchos a muchos (`Movie.directores`, el actor que dirige la película)
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


class Genre(models.Model):
    """Género cinematográfico (tabla de catálogo)."""

    nombre = models.CharField(max_length=50, unique=True, verbose_name='nombre')
    descripcion = models.TextField(blank=True, verbose_name='descripción')

    class Meta:
        verbose_name = 'género'
        verbose_name_plural = 'géneros'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Person(models.Model):
    """Persona del equipo creativo (director/a)."""

    nombre = models.CharField(max_length=100, verbose_name='nombre')
    apellidos = models.CharField(max_length=100, verbose_name='apellidos')
    fecha_nacimiento = models.DateField(
        null=True, blank=True, verbose_name='fecha de nacimiento'
    )
    pais = models.CharField(max_length=60, blank=True, verbose_name='país')
    foto = models.ImageField(
        upload_to='personas/', blank=True, null=True, verbose_name='foto'
    )

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f'{self.nombre} {self.apellidos}'.strip()


class Movie(models.Model):
    """Película: se relaciona con los géneros (M2M) y con sus valoraciones (FK inversa)."""

    titulo = models.CharField(max_length=200, verbose_name='título')
    anio = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
        verbose_name='año',
    )
    duracion = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='duración (minutos)'
    )
    sinopsis = models.TextField(blank=True, verbose_name='sinopsis')
    cartel = models.ImageField(
        upload_to='carteles/', blank=True, null=True, verbose_name='cartel'
    )

    # Paso 2 - muchos a muchos con los géneros
    generos = models.ManyToManyField(
        Genre, related_name='peliculas', blank=True, verbose_name='géneros'
    )
    directores = models.ManyToManyField(
        Person, related_name='peliculas_dirigidas', blank=True, verbose_name='directores'
    )

    # Paso 7 - campos de auditoría (auto_now_add / auto_now)
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name='fecha de creación'
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True, verbose_name='fecha de última modificación'
    )

    class Meta:
        verbose_name = 'película'
        verbose_name_plural = 'películas'
        ordering = ['-anio', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.anio})'

    @property
    def valoracion_media(self):
        """Media de las puntuaciones de la película (None si no tiene valoraciones)."""
        media = self.valoraciones.aggregate(promedio=Avg('puntuacion'))['promedio']
        return media


class Rating(models.Model):
    """Valoración de una película: FK a Movie (una película, muchas valoraciones)."""

    pelicula = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='valoraciones',
        verbose_name='película',
    )
    critico = models.CharField(max_length=100, verbose_name='crítico')
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='puntuación (1-10)',
    )
    comentario = models.TextField(blank=True, verbose_name='comentario')
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name='fecha de creación'
    )

    class Meta:
        verbose_name = 'valoración'
        verbose_name_plural = 'valoraciones'
        ordering = ['-puntuacion', 'fecha_creacion']
        constraints = [
            models.UniqueConstraint(
                fields=['pelicula', 'critico'],
                name='unique_valoracion_por_critico',
            )
        ]

    def __str__(self):
        return f'{self.pelicula.titulo} - {self.critico}: {self.puntuacion}/10'
