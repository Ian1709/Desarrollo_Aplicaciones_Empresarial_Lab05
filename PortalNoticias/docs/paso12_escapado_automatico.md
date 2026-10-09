# Paso 12 · Escapado automático de plantillas

## Qué se hizo

Se guardó una noticia cuyo **cuerpo** y **resumen** contienen etiquetas HTML
escritas por el redactor:

```
Resumen: Resumen con <b>negrita</b> y <i>cursiva</i> escritas a mano.

Cuerpo:  Este párrafo lo escribió el redactor con una etiqueta
         <b>en negrita</b> y un aviso <script>alert("xss")</script>
         dentro del texto.
```

El comando que lo hace y muestra el resultado:

```powershell
python manage.py demo_escapado
```

La noticia también se puede crear a mano desde el panel en
`/admin/news/article/` (`admin` / `admin123`), pegando el HTML en el campo
**cuerpo** y guardando.

## Qué muestra la página

El detalle de la noticia devuelve el HTML así (`evidencias/paso12_escapado_automatico.txt`):

```html
<div class="noticia-cuerpo">
  <p>Este párrafo lo escribió el redactor con una etiqueta
     &lt;b&gt;en negrita&lt;/b&gt; y un aviso
     &lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt; dentro del texto.</p>
</div>
```

Y en la portada, la tarjeta:

```html
<p class="tarjeta-resumen">Resumen con &lt;b&gt;negrita&lt;/b&gt;
   y &lt;i&gt;cursiva&lt;/i&gt; escritas a mano.</p>
```

Es decir, en el navegador **se ve el texto de las etiquetas** (`<b>`, `<script>`)
en lugar de aplicarse: la "negrita" no pone nada en negrita y el `<script>` no
se ejecuta.

## Por qué ocurre

1. **El autoescapado de Django está activado por defecto** en los templates:
   cada `{{ variable }}` convierte `<`, `>` y `"` en entidades HTML
   (`&lt;`, `&gt;`, `&quot;`) antes de escribir el valor en la página.
2. Como el contenido viene de la base de datos (lo escribió un redactor), Django
   lo trata como **texto no confiable** y lo neutraliza. Sin este comportamiento,
   cualquiera que pudiera escribir una noticia podría inyectar código
   (cross-site scripting, XSS).
3. Para que una etiqueta **sí** se interprete habría que marcarla de forma
   consciente con el filtro `|safe` o `{% autoescape off %}`, decisión que aquí
   **no** se toma a propósito. Prueba de ello:
   `test_la_etiqueta_no_se_interpreta_salvo_que_se_marque_como_segura`.
4. `linebreaks` (usado en el cuerpo) sólo añade párrafos: el texto sigue
   viniendo escapado por dentro.

## Pruebas que lo garantizan

En `news/tests.py`, clase `EscapadoAutomaticoTests`:

| Prueba | Qué comprueba |
| --- | --- |
| `test_el_cuerpo_se_muestra_escapado` | En el detalle aparece `&lt;script&gt;...` y **no** `<script>alert(...)</script>` |
| `test_el_titulo_se_muestra_escapado` | El título con `<b>` se pinta como `&lt;b&gt;` en la portada |
| `test_la_etiqueta_no_se_interpreta_salvo_que_se_marque_como_segura` | Sin `|safe`, `<b>negrita</b>` no se convierte en negrita |

Resultado: `python manage.py test news` → **17 pruebas, OK**.
