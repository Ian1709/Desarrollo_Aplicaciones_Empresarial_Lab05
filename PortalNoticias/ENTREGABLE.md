# Entregable Parte 2 · Portal de Noticias (`PortalNoticias`)

| | |
| --- | --- |
| **Autor** | Ian (`Ian1721`) |
| **Correo** | ian.rau.1721@gmail.com |
| **Fecha** | 2 de octubre de 2026 |
| **Tecnología** | Django 5.2.17, Pillow 12.3.0, Python 3.14.3, SQLite |
| **Repositorio** | https://github.com/Ian1709/Desarrollo_Aplicaciones_Empresarial_Lab05 |
| **Carpeta** | `PortalNoticias/` (segunda parte, junto al Lab 05) |

Segunda parte del trabajo: un **portal de noticias** con el que se practica el
sistema de plantillas de Django (herencia, fragmentos, filtros, `{% url %}`,
estáticos y escapado automático), además del panel de administración.

---

## 1. Cómo ejecutar

```powershell
cd "C:\Users\Ian\Documents\Default Project\Lab05_proyecto\PortalNoticias"
..\.venv\Scripts\Activate.ps1          # reutiliza el entorno del Lab 05
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_noticias --reset
python manage.py demo_escapado         # noticia del Paso 12
python manage.py runserver
```

| URL | Página |
| --- | --- |
| http://127.0.0.1:8000/ | Portada |
| http://127.0.0.1:8000/noticia/2/ | Detalle de una noticia |
| http://127.0.0.1:8000/categoria/cultura/ | Listado por categoría |
| http://127.0.0.1:8000/admin/ | Panel (`admin` / `admin123`) |

Pruebas: `python manage.py test news` → **17 pruebas, OK**.

---

## 2. Estructura

```
PortalNoticias/
├── manage.py
├── requirements.txt          # Django + Pillow
├── config/                   # proyecto (settings, urls, wsgi, asgi)
├── news/
│   ├── models.py             # Article, Category, Author
│   ├── admin.py              # los tres modelos personalizados
│   ├── views.py              # index, article_detail, category_list
│   ├── urls.py               # rutas con nombre (namespace "news")
│   ├── tests.py              # 17 casos de prueba
│   ├── migrations/0001_initial.py
│   └── management/commands/  # cargar_noticias, demo_escapado
├── templates/
│   ├── base.html
│   └── news/
│       ├── index.html
│       ├── article_detail.html
│       ├── category_list.html
│       └── _article_card.html
├── static/css/portal.css
├── media/                    # imágenes subidas (imagen destacada, fotos)
├── capturas/                 # capturas del portal y del panel
├── evidencias/               # salidas de las pruebas y verificaciones
└── docs/paso12_escapado_automatico.md
```

---

## 3. Paso a paso

### Paso 1 · Proyecto, Pillow y app `news`
`django-admin startproject config` crea el paquete de configuración `config/` y
`startapp news` la aplicación. En `config/settings.py` se añade `'news'` a
`INSTALLED_APPS`, se fija `LANGUAGE_CODE = 'es'` y la zona horaria. `requirements.txt`
declara Django y **Pillow** (necesario para `ImageField`).

### Paso 2 · Plantillas, estáticos y medios
- `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']` → directorio de plantillas del proyecto.
- `STATIC_URL`, `STATICFILES_DIRS = [BASE_DIR / 'static']`.
- `MEDIA_URL = 'media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`.
- `config/urls.py` sirve los medios en desarrollo:

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> Nota de mantenimiento: `ALLOWED_HOSTS = ['*']` en desarrollo, porque con la
> lista restrictiva el navegador devolvía **Bad Request (400)** al entrar con
> otra dirección distinta de 127.0.0.1.

### Paso 3 · Modelos, migración y superusuario

| Modelo | Campos propios | Relaciones |
| --- | --- | --- |
| `Category` | `name`, `slug`, `description` | N:M con `Article` |
| `Author` | `name`, `slug`, `email`, `bio`, `photo` | 1:N con `Article` |
| `Article` | `title`, `slug`, `summary`, `body`, **`featured_image`**, **`published_at`** | `author` (FK, `PROTECT`), `categories` (M2M) |

- `published_at` con `default=timezone.now` es la **fecha de publicación**.
- `featured_image` es la **imagen destacada** (`ImageField`, sube a `media/articulos/`).
- Los `slug` se calculan solos con `slugify` al guardar.
- `Meta.ordering = ['-published_at']` en `Article`.
- `on_delete=PROTECT` impide borrar un autor que tiene noticias (probado en un test).

Migración `news/migrations/0001_initial.py` aplicada y superusuario `admin`
creado con un `create_superuser` (contraseña `admin123`).

### Paso 4 · `base.html`
Estructura común del portal con tres bloques que rellenan las páginas:
`{% block title %}`, `{% block content %}` y `{% block sidebar %}` (más un
`{% block menu %}` para la barra de navegación). Cabecera, contenedor con
columna de contenido + barra lateral y pie.

### Paso 5 · Fragmento `_article_card.html`
Tarjeta reutilizable de una noticia: imagen destacada, etiquetas de categoría,
título enlazado, resumen recortado, fecha y autor. Se incluye con
`{% include "news/_article_card.html" with article=article %}`.

### Paso 6 · Portada `index.html`
- `{% for article in articles %}` recorre las noticias (más la destacada del bloque superior).
- `{% empty %}` muestra "No hay noticias publicadas todavía."
- Filtros: la fecha con `{{ destacada.published_at|date:"l, j \d\e F \d\e Y" }}`
  (→ *viernes, 9 de octubre de 2026*) y el resumen con `|truncatewords:20` / `:40`.

### Paso 7 · Detalle `article_detail.html`
Hereda de `base.html` y muestra la **imagen** destacada en un `<figure>`, el
**autor** con foto y biografía, las **categorías** y el cuerpo con `|linebreaks`.

### Paso 8 · Listado `category_list.html`
Muestra las noticias de una categoría reutilizando **el mismo fragmento**
`_article_card.html` que la portada.

### Paso 9 · Rutas con nombre y `{% url %}`
`news/urls.py` con `app_name = 'news'`:

```python
path('', views.index, name='index'),
path('noticia/<int:pk>/', views.article_detail, name='article_detail'),
path('categoria/<slug:slug>/', views.category_list, name='category_list'),
```

Todas las plantillas enlazan con `{% url 'news:index' %}`,
`{% url 'news:article_detail' article.pk %}` y
`{% url 'news:category_list' category.slug %}`: **no queda ninguna dirección
escrita a mano** (comprobado con una búsqueda en `templates/`).

### Paso 10 · Estáticos
`base.html` carga `{% load static %}` y `static/css/portal.css`. Verificado por
HTTP (`evidencias/paso10_13_verificacion_portal.txt`):

| Recurso | HTTP | Tipo |
| --- | --- | --- |
| `/static/css/portal.css` | 200 | `text/css` |
| `/media/articulos/noticia-1.png` | 200 | `image/png` |

### Paso 11 · Panel personalizado y datos

- `CategoryAdmin`: `list_display = (name, slug, num_articles)`, `search_fields`, `prepopulated_fields`.
- `AuthorAdmin`: `list_display = (name, email, num_articles)`, `search_fields`.
- `ArticleAdmin`: `list_display = (title, author, categorías, published_at)`,
  `list_filter = (published_at, author, categories)`,
  `search_fields = (title, summary, body, author__name)`,
  `date_hierarchy = 'published_at'` y `filter_horizontal = ('categories',)`.

El comando `python manage.py cargar_noticias --reset` crea **3 categorías**
(Política, Deportes, Cultura), 2 autores y **6 noticias** (2 por categoría) con
imágenes generadas con Pillow. Comprobado que aparecen en el portal: la portada
pinta 7 tarjetas (6 + la destacada) y cada categoría responde 200 con sus noticias.

### Paso 12 · Escapado automático
Se guarda una noticia con etiquetas HTML en el cuerpo y el resumen
(`<b>`, `<script>alert("xss")</script>`). Informe completo en
`docs/paso12_escapado_automatico.md`; resumen:

- La base de datos guarda el texto **tal cual**, con sus etiquetas.
- La página **no las interpreta**: devuelve `&lt;b&gt;`, `&lt;script&gt;`,
  `&quot;...&quot;`. El navegador muestra las etiquetas como texto y **no
  ejecuta** el script.
- Motivo: Django activa el **autoescapado** en las plantillas, de modo que un
  dato que viene de la base de datos se trata como no confiable. Para que una
  etiqueta se interpretara habría que marcarla con `|safe` o
  `{% autoescape off %}`, cosa que **no** se hace.

### Paso 13 · Entrega
Este documento, las capturas de `capturas/`, el código y los casos de prueba
(`news/tests.py`) se suben al repositorio del equipo y al campus virtual.

---

## 4. Capturas

Están en `capturas/` (generadas con Edge en modo headless sobre el servidor real):

| Captura | Qué muestra |
| --- | --- |
| `01_portada.png` | Portada con la noticia destacada y las tarjetas, ya con estilos e imágenes |
| `02_detalle_noticia.png` | Detalle con imagen, autor, categorías y cuerpo |
| `03_listado_por_categoria.png` | Listado de la categoría *Cultura* reutilizando la tarjeta |
| `04_escapado_automatico.png` | Detalle de la noticia con HTML: se ven las etiquetas escapadas |
| `06_admin_indice.png` | Índice del panel con los tres modelos |
| `07_admin_noticias_listado.png` | Listado de noticias con columnas, filtros y buscador |
| `08_admin_busqueda.png` | Búsqueda "selecci" en el listado |
| `09_admin_filtro_fecha.png` | Filtro por fecha de publicación |
| `10_admin_noticia_formulario.png` | Formulario de la noticia con selector de categorías |
| `11_admin_categorias.png` | Listado de categorías con el número de noticias |
| `12_admin_autores.png` | Listado de autores con el número de noticias |

---

## 5. Casos de prueba

`python manage.py test news` → **17 pruebas** (`evidencias/pruebas_automaticas.txt`):

| Clase | Qué cubre |
| --- | --- |
| `ModelosTests` (6) | `__str__`, slugs automáticos, M2M de categorías, orden por fecha, `PROTECT` del autor y `get_absolute_url` |
| `VistasTests` (6) | Portada, detalle con autor y categorías, listado por categoría, 404 de categoría y de noticia, y enlaces generados con `{% url %}` |
| `EscapadoAutomaticoTests` (3) | El cuerpo y el título se muestran escapados; sin `|safe` la etiqueta no se interpreta |
| `AdminTests` (2) | Los tres modelos registrados y el listado con buscador y filtros |

---

## 6. Evidencias

| Archivo | Contenido |
| --- | --- |
| `evidencias/pruebas_automaticas.txt` | Salida de las 17 pruebas |
| `evidencias/paso10_13_verificacion_portal.txt` | Estado HTTP de páginas, CSS y medios, contenido de la portada y escapado |
| `evidencias/paso12_escapado_automatico.txt` | Qué guarda la BD y qué devuelve la página con HTML |

---

## 7. Historial de commits (Parte 2)

| Commit | Paso |
| --- | --- |
| `Paso 1` | Proyecto `config`, Pillow y app `news` |
| `Paso 2` | Plantillas, estáticos y medios; servir medios en `config/urls.py` |
| `(fix)` | `ALLOWED_HOSTS` para corregir el Bad Request (400) |
| `Paso 3` | Modelos `Article`, `Category`, `Author`, migración y superusuario |
| `Paso 4` | `base.html` con los bloques |
| `Paso 5` | Fragmento `_article_card.html` |
| `Paso 6` | Portada con `for`, `empty` y filtros de fecha y recorte |
| `Paso 7` | Detalle de la noticia |
| `Paso 8` | Listado por categoría con el fragmento |
| `Paso 9` | Rutas con nombre y enlaces con `{% url %}` |
| `Paso 10` | Estáticos con `{% load static %}` y comprobación |
| `Paso 11` | Admin personalizado y seis noticias en tres categorías |
| `Paso 12` | Escapado automático con pruebas y documentación |
| `Paso 13` | Entregable, capturas y publicación |

---

## 8. Limitaciones

- El portal usa SQLite y `DEBUG=True`; para producción faltarían
  `DEBUG=False`, `SECRET_KEY` de entorno, `ALLOWED_HOSTS` real y servidor de
  estáticos.
- El buscador de texto es un `icontains` de Django; no hay búsqueda por relevancia.
- Las imágenes se generan con Pillow para que el repositorio no dependa de
  archivos externos; en un portal real las subiría el redactor.
- La noticia del Paso 12 convive con las seis del Paso 11; por eso la portada
  muestra siete tarjetas.
