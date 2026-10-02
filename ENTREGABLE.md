# Entregable Lab 05 - Panel de administración de cine y recomendación de películas

| | |
| --- | --- |
| **Autor** | Ian (`Ian1709`) |
| **Correo** | ian.rau.1721@gmail.com |
| **Fecha** | 2 de octubre de 2026 |
| **Tecnología** | Django 5.2.17, Pillow 12.3.0, Python 3.14.3, SQLite |
| **Repositorio** | https://github.com/Ian1709/Desarrollo_Aplicaciones_Empresarial_Lab05 |
| **Rama** | `main` |

---

## 1. Necesidad y objetivo

El cliente es un cine que necesita:

1. **Mantener el catálogo y las valoraciones de la crítica** desde un panel de
   administración donde el alta de una película incluya sus puntuaciones, sin
   tener que entrar en otro formulario.
2. **Controlar quién puede tocar los datos**: que un editor pueda añadir y
   modificar películas, pero no destruirlas.
3. **Saber que nadie altera la trazabilidad**: las fechas de alta y de última
   modificación se muestran pero no se escriben a mano.
4. **Responder "¿qué me recomiendas?"**: el panel sirve para mantener los datos,
   pero la recomendación es una consulta que necesita su propia vista.

El objetivo de la aplicación es cubrir los cuatro puntos: panel personalizado
(Pasos 1-7), carga de datos reales usando ese panel (Paso 8), permisos por grupo
(Paso 9) y una vista pública de recomendación (Paso 10).

---

## 2. Modelos de datos

| Modelo | Campos | Relaciones |
| --- | --- | --- |
| `Genre` | `nombre`, `descripcion` | 1:N con `Movie` (M2M) |
| `Person` | `nombre`, `apellidos`, `fecha_nacimiento`, `pais`, `foto` | M2M como director |
| `Movie` | `titulo`, `anio`, `duracion`, `sinopsis`, `cartel`, `fecha_creacion`, `fecha_modificacion` | M2M `generos`, M2M `directores` |
| `Rating` | `pelicula`, `critico`, `puntuacion` (1-10), `comentario`, `fecha_creacion` | N:1 con `Movie` (`on_delete=CASCADE`), único por película y crítico |

Decisiones relevantes:

- `Meta.ordering` por `nombre` en `Genre` y por `titulo`/`-anio` en `Movie`, y
  `-puntuacion` en `Rating`, para que listados y fichas salgan ordenados sin
  código extra.
- `@property valoracion_media` en `Movie` (media de las valoraciones) y
  `@property valoracion_texto` para pintar "sin valorar" cuando no hay notas.
- `unique_together = ('pelicula', 'critico')`: el mismo crítico no valora dos
  veces la misma película.
- `CASCADE` hace que al borrar una película desaparezcan sus valoraciones
  (verificado en `test_borrar_pelicula_borra_sus_valoraciones`).
- `cartel` y `foto` usan `ImageField`, lo que obliga a instalar Pillow (Paso 1)
  y a servir `MEDIA_URL` en desarrollo (Paso 3).

Migración `0001_initial.py` aplicada y verificada en
`evidencias/verificar_migraciones.txt`.

---

## 3. Panel de administración: antes y después

Las capturas están en `capturas/`. El "antes" se obtuvo levantando el commit
del Paso 4 (`67a05ae`, registro simple de los cuatro modelos) con los mismos
datos, de modo que la comparación sea justa.

| Captura | Qué muestra |
| --- | --- |
| `01_antes_indice_panel.png` | Índice del panel con los cuatro modelos (registro simple) |
| `02_antes_listado_peliculas.png` | Listado de películas por defecto: una sola columna (`__str__`), sin filtros y **sin buscador** |
| `03_antes_formulario_pelicula.png` | Formulario de película sin inline de valoraciones y sin fechas de auditoría |
| `04_despues_indice_panel.png` | Índice del panel tras la personalización |
| `05_despues_listado_peliculas.png` | Listado con 6 columnas, filtro por género, filtro por década y buscador |
| `06_despues_filtro_genero_misterio.png` | Listado filtrado por el género *Misterio* (4 películas) |
| `07_despues_busqueda_titulo.png` | Búsqueda por título "pulp" (1 resultado) |
| `08_despues_formulario_con_inline.png` | Formulario de *Inception* con inline de valoraciones y fechas en solo lectura |
| `09_editor_indice_panel.png` | Sesión `editor`: en el índice solo aparece *Películas* |
| `10_editor_listado_peliculas.png` | Listado del editor: sin acción "Eliminar" y sin casillas de selección |
| `11_editor_formulario_pelicula.png` | Formulario del editor: sin botón eliminar y sin inline de valoraciones |
| `12_publico_catalogo_recomendaciones.png` | Vista pública `/`: mejores valoradas de cada género + catálogo |
| `13_publico_ficha_con_recomendacion.png` | Vista pública `/pelicula/3/`: ficha con "Te puede interesar" |

Contenido real de cada captura verificado sobre el HTML servido por el panel
(`evidencias/paso11_contenido_capturas.txt`):

| Comprobación | Antes (Paso 4) | Después (final) |
| --- | --- | --- |
| Columnas del listado de películas | `['__str__']` | `titulo, anio, generos_texto, directores_texto, num_valoraciones, valoracion_media` |
| Filtros del listado | ninguno | género (`generos__id__exact`, `generos__isnull`) y década (`decada`) |
| Buscador (`name="q"`) | no | sí |
| Inline de valoraciones | no | sí |
| Fechas de auditoría | no aparecen | aparecen y **no** son inputs editables |
| Acción "Eliminar" del listado | disponible | disponible solo para quien tiene `delete_movie` |
| Índice del panel con `editor` | 4 modelos | solo *Películas* |

> Nota: `01` y `04` son idénticas porque el índice del panel ya mostraba los
> cuatro modelos tras el simple registro del Paso 4; la personalización se aprecia
> en el listado y en el formulario, que son las capturas `02/03` frente a
> `05/06/07/08`.

Cambios concretos en `movies/admin.py`:

- `MovieAdmin.list_display`: título, año, géneros, directores, número de
  valoraciones y valoración media.
- `MovieAdmin.list_filter`: filtro por género (`list_filter` con
  `filter_horizontal`) y filtro propio `FiltroAnio` por década.
- `MovieAdmin.search_fields`: `titulo`, `sinopsis`, `directores__nombre`,
  `directores__apellidos`.
- `MovieAdmin.readonly_fields`: `fecha_creacion`, `fecha_modificacion`.
- `MovieAdmin.inlines`: `RatingInline` con `extra = 1` para proponer una
  valoración nueva.
- `GenreAdmin`, `PersonAdmin` y `RatingAdmin` con sus propias columnas, filtros
  y búsqueda.

---

## 4. Carga de datos usando el panel (Paso 8)

`movies/management/commands/cargar_datos_panel.py` **no inserta filas con el
ORM**: se inicia sesión contra el panel y se envían formularios por HTTP al
mismo endpoint que usa el navegador (`/admin/movies/<modelo>/add/`), incluido el
inline de valoraciones. Con `--reset` borra primero los datos existentes.

```powershell
python manage.py cargar_datos_panel --reset
```

Resultado (salida completa en `evidencias/paso8_carga_datos_panel.txt`):

- 4 géneros: Aventura, Drama, Ciencia ficción, Misterio.
- 5 personas: 3 directores y 2 hibernadas/actrices de apoyo.
- 10 películas de 1993 a 2010, con cartel para *Inception* generado con Pillow.
- 12 valoraciones, 7 de ellas sobre películas distintas (2 en *Inception* para
  poder ver el inline con varias filas).

Comprobado que los datos se pueden mantener después desde el panel: crear una
película con valoración desde `/admin/movies/movie/add/` y editarla.

---

## 5. Permisos: superusuario frente a editor (Paso 9)

`movies/management/commands/crear_grupo_editores.py` crea el grupo `editores`
con **exactamente** tres permisos:

| Permiso | Otorgado |
| --- | --- |
| `movies.add_movie` | sí |
| `movies.change_movie` | sí |
| `movies.view_movie` | sí |
| `movies.delete_movie` | **no** |

Comparativa verificada sobre el panel (`evidencias/paso9_comparativa_admin_vs_editor.txt`):

| Comprobación | `admin` (superusuario) | `editor` (grupo `editores`) |
| --- | --- | --- |
| Modelos en el índice | Géneros, Películas, Personas, Valoraciones | solo Películas |
| `/admin/movies/movie/` | 200 | 200 |
| `/admin/movies/movie/add/` | 200 | 200 |
| `/admin/movies/movie/<id>/change/` | 200 | 200 |
| `/admin/movies/movie/<id>/delete/` | 200 (puede borrar) | **403** |
| Acción "Eliminar" en el listado | disponible | **no aparece** |
| Inline de valoraciones | visible | **no visible** |
| `/admin/movies/genre/`, `/person/`, `/rating/` | 200 | **403** |
| `is_superuser` | `True` | `False` |

Justificación: el editor es el perfil que incorpora/reviews las fichas del
catálogo; puede proponer y corregir películas, pero la eliminación de datos es una
decisión del responsable del cine y por eso exige superusuario.

---

## 6. Vista pública de recomendación (Paso 10)

`movies/views.py`:

- `movie_list`: todas las películas con su media, ordenadas de mejor a peor
  valoración.
- `mejores_por_genero(limite=3)`: para cada género, las tres películas mejor
  valoradas. Es el bloque "Recomendaciones" de la portada.
- `movie_detail`: ficha con sus valoraciones y recomendaciones.
- `recommender(pelicula, limite=5)`: **las películas que comparten al menos un
  género con la película abierta, mejor valoradas y excluyendo ella misma**
  (`generos__in`, `Avg('valoraciones__puntuacion')`, `HAVING COUNT > 0`,
  `LIMIT 5`).

Salida real con los datos del laboratorio
(`evidencias/paso10_vista_recomendacion.txt`):

```
Ciencia ficción -> 2001: Una odisea espacial (9.00), Inception (8.50), Gravity (7.50)
Drama           -> La lista de Schindler (10.00), Pulp Fiction (9.50), El resplandor (8.00)
Misterio        -> Pulp Fiction (9.50), Inception (8.50), Interest (8.00)

Inception [Ciencia ficción, Misterio]
    -> Pulp Fiction (9.50), 2001 (9.00), Interest (8.00), El resplandor (8.00), Gravity (7.50)
Parque Jurásico [Aventura]
    -> (ninguna: no hay otra película de Aventura valorada)
```

SQL generado por Django para la ficha de *Inception* (incluido en la evidencia):

```sql
SELECT DISTINCT "movies_movie"."id", ..., AVG("movies_rating"."puntuacion") AS "media",
       COUNT(DISTINCT "movies_rating"."id") AS "num_valoraciones"
FROM "movies_movie"
INNER JOIN "movies_movie_generos" ON ("movies_movie"."id" = "movies_movie_generos"."movie_id")
LEFT OUTER JOIN "movies_rating" ON ("movies_movie"."id" = "movies_rating"."pelicula_id")
WHERE ("movies_movie_generos"."genre_id" IN (3, 2) AND NOT ("movies_movie"."id" = 3))
GROUP BY ...
HAVING COUNT(DISTINCT "movies_rating"."id") > 0
ORDER BY 9 DESC, 10 DESC, "movies_movie"."anio" DESC
LIMIT 5
```

Esta consulta es exactamente lo que el panel **no** puede ofrecer: el panel
gestiona filas, no relaciones de valor entre filas.

---

## 7. Pruebas automáticas

```powershell
python manage.py test movies
```

**19 pruebas, todas en verde** (`evidencias/pruebas_automaticas.txt`):

| Clase | Qué cubre |
| --- | --- |
| `MovieModelTests` (4) | `__str__` de los cuatro modelos, M2M de géneros, 1:N de valoraciones, `CASCADE` al borrar la película |
| `AdminPanelTests` (5) | los cuatro modelos registrados, listado y alta de cada uno, inline presente en el formulario, fechas de auditoría no editables, alta de una película con valoración desde el panel, búsqueda y filtros |
| `EditorPermisosTests` (4) | el editor no tiene `delete_movie`, ve el listado y el formulario pero recibe 403 al borrar, no ve los otros tres modelos, el superusuario sí puede borrar |
| `RecomendacionViewTests` (5) | orden del catálogo, recomendación del mismo género y mejor valorada, exclusión de la propia película y de las que no comparten género, película sin géneros, agrupación por género y 404 |

---

## 8. Evidencias

| Archivo | Contenido |
| --- | --- |
| `evidencias/verificar_migraciones.txt` | Aplicación de migraciones y superusuario |
| `evidencias/tablas_y_superusuario.txt` | Tablas creadas y usuarios (Paso 3) |
| `evidencias/admin_paso4_registro_simple.txt` | Panel tras registrar los modelos |
| `evidencias/admin_paso5_modeladmin.txt` | Columnas, filtros y búsqueda |
| `evidencias/admin_paso6_inline.txt` | Inline de valoraciones |
| `evidencias/admin_paso7_readonly.txt` | Fechas en solo lectura |
| `evidencias/paso8_carga_datos_panel.txt` | Carga por formularios del panel |
| `evidencias/paso9_grupo_editores.txt` | Permisos del grupo `editores` |
| `evidencias/paso9_comparativa_admin_vs_editor.txt` | Comparativa de accesos |
| `evidencias/paso10_vista_recomendacion.txt` | Recomendaciones por género, por película y SQL |
| `evidencias/pruebas_automaticas.txt` | Salida completa de las 19 pruebas |
| `evidencias/paso11_contenido_capturas.txt` | Qué muestra cada captura, comprobado sobre el HTML |

Los scripts que generan estas salidas están en `evidencias/*.py` y se ejecutan
con `python evidencias/<script>.py` (necesitan `python manage.py runserver` en
algunos casos).

---

## 9. Cómo ejecutar el proyecto

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py cargar_datos_panel --reset
python manage.py crear_grupo_editores
python manage.py runserver
```

- Panel: <http://127.0.0.1:8000/admin/> (`admin` / `admin123`,
  `editor` / `editor123`).
- Catálogo: <http://127.0.0.1:8000/>
- Ficha: <http://127.0.0.1:8000/pelicula/3/> (Inception)
- Pruebas: `python manage.py test movies`

`db.sqlite3` y `media/` están en `.gitignore` a propósito: son datos locales.
Quien clone el repositorio los regenera con los dos comandos de arriba.

---

## 10. Historial de commits

| Commit | Paso |
| --- | --- |
| `81a47f7` | 1. Proyecto Django, Pillow y app `movies` en `INSTALLED_APPS` |
| `5950e47` | 2. Modelos `Movie`, `Genre`, `Person` y `Rating` |
| `37fbeb5` | 3. Migración aplicada, superusuario y configuración de medios |
| `67a05ae` | 4. Registro de los cuatro modelos en el panel |
| `4245462` | 5. `ModelAdmin` con columnas, filtros y búsqueda |
| `0629e2f` | 6. `RatingInline` |
| `f9b184b` | 7. Auditoría en solo lectura |
| `7bb3875` | 8. Carga de datos desde los formularios del panel |
| `c5b3018` | 9. Grupo `editores` y comparativa de permisos |
| `5f5e264` | 10. Vista pública de recomendación, plantillas y 19 pruebas |
| `HEAD` | 11. Entregable, capturas y evidencia de las capturas |

---

## 11. Limitaciones y trabajo pendiente

- Las capturas se generaron automáticamente con Edge en modo headless sobre
  los dos servidores locales; son imágenes reales del panel, pero con la
  tipografía y el tamaño de ventana por defecto del navegador.
- El cartel solo se generó para *Inception* (con Pillow). Las demás películas no
  tienen imagen, que es un estado válido del formulario.
- `FiltroAnio` incluye "anteriores" (antes de 2000) junto con la década de los
  90, de modo que hay solapamiento entre dos opciones del filtro.
- El proyecto usa SQLite y `DEBUG` de desarrollo; para producción faltaría
  `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` real y una base de datos de
  servidor.
- El entregable no se subió al campus virtual: se dejó como documento local
  (`ENTREGABLE.md` y `capturas/`) para que se suba a mano.