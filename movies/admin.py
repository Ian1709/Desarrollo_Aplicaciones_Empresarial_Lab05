from django.contrib import admin

from .models import Genre, Movie, Person, Rating

# Paso 4 - registro simple: aparecen las cuatro operaciones del panel
# (listado, alta, edición y borrado) sin escribir ninguna vista.
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(Rating)
