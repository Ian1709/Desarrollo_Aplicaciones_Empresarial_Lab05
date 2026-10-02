# Lab 05 - Panel de administración de cine y recomendación de películas

**Proyecto:** `Lab05_proyecto` (Django 5.2 + SQLite)
**Autor:** Ian (usuario de GitHub `Ian1709`)
**Fecha:** 2 de octubre de 2026
**Repositorio:** https://github.com/Ian1709/Desarrollo_Aplicaciones_Empresarial_Lab05

## Qué resuelve

Un cine necesita mantener su catálogo (películas, géneros, personas) y las
valoraciones de la crítica desde un panel de administración, y además necesita
responder una pregunta que el panel no puede contestar: **"¿qué me recomiendas?"**.

- **Pasos 1-9**: aplicación Django con cuatro modelos, panel de administración
  personalizado, carga de datos **usando los formularios del propio panel**
  (no con SQL ni con fixtures), auditoría en solo lectura y un grupo de
  editores sin permiso de borrado.
- **Paso 10**: vista pública de recomendación: películas del mismo género mejor
  valoradas, calculada con `Avg` sobre las valoraciones.
- **Paso 11**: evidencias, capturas del panel antes/después y comparativa de
  permisos.

## Requisitos

- Python 3.14.3
- Django >= 5.2, < 6.0
- Pillow >= 12.0

## Instalación y ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py cargar_datos_panel --reset     # datos del Paso 8
python manage.py crear_grupo_editores           # grupo y usuario del Paso 9
python manage.py createsuperuser               # admin / admin123
python manage.py runserver
```

| URL | Contenido |
| --- | --- |
| `/admin/` | Panel de administración |
| `/` | Catálogo con recomendaciones por género |
| `/pelicula/<id>/` | Ficha de la película con "Te puede interesar" |

**Cuentas de la demo** (creadas por los comandos del laboratorio):

| Cuenta | Clave | Permisos |
| --- | --- | --- |
| `admin` | `admin123` | Superusuario |
| `editor` | `editor123` | Grupo `editores`: añadir, cambiar y ver películas; **no** puede borrar |

## Estructura

```
Lab05_proyecto/
├── manage.py
├── requirements.txt
├── Lab05_proyecto/          # settings.py, urls.py, wsgi.py, asgi.py
├── movies/
│   ├── models.py            # Movie, Genre, Person, Rating
│   ├── admin.py             # ModelAdmin, filtros, RatingInline, solo lectura
│   ├── views.py             # movie_list, movie_detail, recommender
│   ├── urls.py              # / y /pelicula/<pk>/
│   ├── tests.py             # 19 pruebas automáticas
│   ├── migrations/0001_initial.py
│   ├── templates/movies/    # base.html, movie_list.html, movie_detail.html
│   └── management/commands/ # cargar_datos_panel, crear_grupo_editores
├── capturas/                # 13 capturas del panel y de las vistas públicas
└── evidencias/              # salida de las comprobaciones paso a paso
```

## Datos cargados

4 géneros, 5 personas, 10 películas, 12 valoraciones (7 películas con nota media) y un
cartel generado con Pillow.

## Pruebas

```powershell
python manage.py test movies
```

19 pruebas: modelos y relaciones, panel (registro, inline, solo lectura, alta
con valoraciones, búsqueda y filtros), permisos del grupo `editores` y vistas
públicas de recomendación.

## Evidencias

- `ENTREGABLE.md`: informe completo con capturas antes/después y comparativa.
- `evidencias/`: salidas de cada paso, incluidas las pruebas automáticas.
- `capturas/`: imágenes del panel y de la vista pública.

## Commits

| Commit | Paso |
| --- | --- |
| `81a47f7` | 1. Proyecto, Pillow y app `movies` |
| `5950e47` | 2. Modelos `Movie`, `Genre`, `Person`, `Rating` |
| `37fbeb5` | 3. Migración, superusuario y medios |
| `67a05ae` | 4. Registro de los cuatro modelos en el panel |
| `4245462` | 5. `ModelAdmin`: columnas, filtros y búsqueda |
| `0629e2f` | 6. `RatingInline` |
| `f9b184b` | 7. Auditoría en solo lectura |
| `7bb3875` | 8. Carga de datos desde los formularios del panel |
| `c5b3018` | 9. Grupo `editores` y comparativa de permisos |
| `5f5e264` | 10. Vista pública de recomendación y pruebas |
| `5e3ade9` | 11. Entregable y capturas del panel |
| (último) | 12. Publicación en `origin/main` |