"""Verificación del portal y del panel sirviéndose por HTTP (Pasos 10, 11 y 13).

Necesita el servidor en marcha:

    python manage.py runserver 127.0.0.1:8020
    python evidencias/verificar_portal.py http://127.0.0.1:8020

Usa sólo la librería estándar (urllib), así que funciona con el .venv del proyecto.
"""

import re
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8020'

PAGINAS = [
    ('Portada', '/', 'Últimas noticias'),
    ('Detalle de noticia', '/noticia/2/', 'noticia-cuerpo'),
    ('Listado por categoría', '/categoria/cultura/', 'class="tarjeta"'),
    ('Hoja de estilos', '/static/css/portal.css', '--acento'),
    ('Imagen destacada (media)', '/media/articulos/noticia-1.png', None),
    ('Panel: noticias', '/admin/news/article/', None),
    ('Panel: categorías', '/admin/news/category/', None),
    ('Panel: autores', '/admin/news/author/', None),
]


def obtener(ruta):
    peticion = urllib.request.Request(f'{BASE}{ruta}', headers={'User-Agent': 'verificador'})
    with urllib.request.urlopen(peticion) as respuesta:
        return respuesta.status, respuesta.headers.get('Content-Type', ''), respuesta.read()


def main():
    print('VERIFICACIÓN DEL PORTAL DE NOTICIAS')
    print('=' * 72)
    print(f'Servidor: {BASE}')
    print()
    print(f'{"Página":<28}{"Ruta":<32}{"HTTP":<6}{"Tipo"}')
    print('-' * 72)

    ultimo_html = ''
    for nombre, ruta, esperado in PAGINAS:
        try:
            estado, tipo, cuerpo = obtener(ruta)
        except urllib.error.HTTPError as error:
            estado, tipo, cuerpo = error.code, '', b''
        except urllib.error.URLError as error:
            print(f'{nombre:<28}{ruta:<32}ERROR: {error}')
            continue
        marca = ''
        if esperado:
            texto = cuerpo.decode('utf-8', 'replace')
            if esperado in texto:
                marca = ' (contiene lo esperado)'
            else:
                marca = f' (FALTA: {esperado!r})'
            ultimo_html = ultimo_html or texto
        print(f'{nombre:<28}{ruta:<32}{estado:<6}{tipo}{marca}')

    print()
    print('CONTENIDO DEL PORTAL (Paso 6: for/empty, filtros date y truncate)')
    print('-' * 72)
    portada = obtener('/')[2].decode('utf-8', 'replace')
    print(f'  destacada presente      : {"destacada" in portada}')
    print(f'  tarjetas de noticia     : {portada.count("class=\"tarjeta\"")}')
    print(f'  caso empty en la vista  : {"No hay noticias publicadas" in portada}')
    fechas = re.findall(r'(\d{1,2} de \w+ de \d{4})', portada)
    print(f'  fechas formateadas      : {fechas[:3]}')
    enlaces = 'href="/noticia/' in portada
    print(f'  enlaces a noticias      : {enlaces}')

    print()
    print('PASO 12: ESCAPADO EN EL DETALLE DE LA NOTICIA CON HTML')
    print('-' * 72)
    detalle = obtener('/noticia/8/')[2].decode('utf-8', 'replace')
    print(f'  aparece &lt;script&gt;  : {"&lt;script&gt;" in detalle}')
    print(f'  aparece <script> real   : {"<script>alert" in detalle}')


if __name__ == '__main__':
    main()
