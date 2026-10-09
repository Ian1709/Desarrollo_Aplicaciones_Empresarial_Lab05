from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """Sección del portal (Política, Deportes, Cultura...)."""

    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField('slug', max_length=90, unique=True, blank=True)
    description = models.TextField('descripción', blank=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    """Periodista que firma las noticias."""

    name = models.CharField('nombre', max_length=120)
    slug = models.SlugField('slug', max_length=140, unique=True, blank=True)
    email = models.EmailField('correo', blank=True)
    bio = models.TextField('biografía', blank=True)
    photo = models.ImageField('foto', upload_to='autores/', blank=True, null=True)

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Noticia publicada en el portal."""

    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=220, unique=True, blank=True)
    summary = models.TextField('resumen', help_text='Entradilla que se muestra en el listado.')
    body = models.TextField('cuerpo')
    featured_image = models.ImageField('imagen destacada', upload_to='articulos/', blank=True, null=True)
    published_at = models.DateTimeField('fecha de publicación', default=timezone.now)
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name='articles', verbose_name='autor'
    )
    categories = models.ManyToManyField(
        Category, related_name='articles', verbose_name='categorías'
    )

    class Meta:
        verbose_name = 'noticia'
        verbose_name_plural = 'noticias'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article_detail', args=[self.pk])
