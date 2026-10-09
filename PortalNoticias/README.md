# Portal de Noticias (`PortalNoticias`)

Segunda parte del trabajo: un portal de noticias en **Django 5.2 + Pillow** que
practica el sistema de plantillas (herencia, fragmentos, filtros, `{% url %}`,
estáticos y escapado automático) y el panel de administración.

## Puesta en marcha

```powershell
cd PortalNoticias
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_noticias --reset   # 3 categorías, 2 autores, 6 noticias
python manage.py demo_escapado             # noticia del Paso 12
python manage.py runserver
```

| URL | Página |
| --- | --- |
| `/` | Portada |
| `/noticia/<id>/` | Detalle de la noticia |
| `/categoria/<slug>/` | Listado por categoría |
| `/admin/` | Panel (`admin` / `admin123`) |

## Pruebas

```powershell
python manage.py test news     # 17 pruebas
```

## Modelos

- `Category`: nombre, slug, descripción — N:M con `Article`.
- `Author`: nombre, slug, correo, biografía, foto — 1:N con `Article`.
- `Article`: título, slug, resumen, cuerpo, **imagen destacada**,
  **fecha de publicación**, autor (FK `PROTECT`) y categorías (M:N).

## Estructura

```
PortalNoticias/
├── config/           # settings, urls, wsgi, asgi
├── news/             # modelos, admin, vistas, urls, tests, comandos
├── templates/        # base.html + news/
├── static/css/       # portal.css
├── media/            # imágenes subidas
├── capturas/         # capturas del portal y del panel
├── evidencias/       # pruebas y verificaciones
├── docs/             # informe del escapado automático
└── ENTREGABLE.md     # informe completo
```

Informe detallado: [`ENTREGABLE.md`](ENTREGABLE.md).
