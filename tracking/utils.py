# tracking/utils.py
import calendar

import folium
from fastkml import kml
from django.conf import settings
from pathlib import Path

def get_color(index):
    """Función para obtener un color basado en el índice."""
    colors = [
        '#ff8781', '#ffd6a5', '#ffbd66', '#db7093', '#b8860b',
        '#9bf6ff', '#a0c4ff', '#bdb2ff', '#ffc6ff', '#cd5c50',
        '#ffca3a', '#8ac926', '#1982c4', '#6a4c93', '#5f9ea0',
        '#bc8f8f', '#ff4500', '#9370db', '#779899',
    ]
    return colors[index % len(colors)]

def crear_mapa_tracking():
    # Crear el mapa centrado en Neuquén, Argentina
    mapa = folium.Map(location=[-39.044, -67.579], zoom_start=10)

    # Construir la ruta del archivo KML usando Path
    kml_file_path = Path(settings.BASE_DIR) / 'NetLogistK' / 'ZonasCI.kml'

    # Cargar el archivo KML utilizando fastkml
    with open(kml_file_path, 'rt', encoding='utf-8') as f:
        kml_content = f.read()

    # Procesar el archivo KML
    k = kml.KML()
    k.from_string(kml_content)

    # Extraer las coordenadas de las áreas o puntos dentro del KML y asignar colores
    index = 0
    for feature in list(k.features()):
        for placemark in feature.features():
            geometry = placemark.geometry
            color = get_color(index)  # Asignar un color basado en el índice

            # Si es un polígono, recorrer el exterior y agregarlo al mapa con el color
            if geometry.geom_type == 'Polygon':
                exterior_coords = list(geometry.exterior.coords)
                folium.Polygon(
                    locations=[(lat, lon) for lon, lat, *_ in exterior_coords],
                    popup=placemark.name,
                    color=color,  # Color del borde
                    fill=True,
                    fill_color=color,  # Color de relleno
                    fill_opacity=0.4,  # Transparencia del relleno
                ).add_to(mapa)

            # Si es un punto, agregar un marcador en ese lugar
            elif geometry.geom_type == 'Point':
                coord = geometry.coords[0]
                folium.Marker(location=[coord[1], coord[0]], popup=placemark.name).add_to(mapa)
            elif geometry.geom_type == 'LineString':
                coords = list(geometry.coords)
                folium.PolyLine(locations=[(lat, lon) for lon, lat, *_ in coords], popup=placemark.name, color=color).add_to(mapa)

            index += 1  # Incrementar el índice para el próximo elemento

    # Asegurarse de que la carpeta static/tracking exista antes de guardar el archivo
    output_dir = Path(settings.BASE_DIR) / 'NetLogistK' / 'static' / 'tracking'
    output_dir.mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe

    # Guardar el mapa en un archivo HTML dentro de la carpeta static/tracking
    mapa.save(output_dir / 'tracking_mapa.html')



# CALENDARIO DE CRONOGRAMA

# Definir la clase personalizada para el calendario
class CustomHTMLCalendar(calendar.HTMLCalendar):
    def formatweekday(self, day):
        # Definir los días de la semana en español
        weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f'<th class="text-center">{weekdays[day]}</th>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        # Obtener el nombre del mes en español con la primera letra en mayúscula
        month_name = calendar.month_name[themonth].capitalize()
        return f'<tr><th colspan="7" class="text-center">{month_name} {theyear}</th></tr>'

# Función para generar el calendario HTML con el mes y año dados
def generar_calendario_mes(anio, mes):
    cal = CustomHTMLCalendar(calendar.MONDAY)
    # Generar el calendario HTML
    calendario_html = cal.formatmonth(anio, mes)
    
    # Añadir estilos CSS
    return f"""
    <div class="custom-calendar">
        <table class="table table-bordered text-center">
            {calendario_html}
        </table>
    </div>
    """
