"""URL configuration for Lab05_proyecto project.

Incluye el panel de administración (`admin/`) y, en la vista pública que se
escribe en el Paso 10, las rutas de `movies`.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
