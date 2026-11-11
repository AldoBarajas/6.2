"""Genera los PDF finales con ReportLab y los datos empíricos de CSV.

Uso: python codigo/crear_documentos.py
"""
import csv
from pathlib import Path
from statistics import mean
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, PageBreak, Image, KeepTogether, HRFlowable)
from reportlab.pdfgen.canvas import Canvas

BASE = Path(__file__).resolve().parent.parent
OUT = BASE/'documentos'
DATA = BASE/'datos'
CHARTS = BASE/'graficas'
OUT.mkdir(parents=True, exist_ok=True)

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV', FONT))
pdfmetrics.registerFont(TTFont('DV-Bold', FONT_BOLD))
NAVY = colors.HexColor('#183153')
TEAL = colors.HexColor('#127C82')
PALE = colors.HexColor('#ECF5F5')
GRAY = colors.HexColor('#495464')
LIGHT = colors.HexColor('#F2F5F9')
LINE = colors.HexColor('#DCE5ED')

styles = {
 'base': ParagraphStyle('normalx', fontName='DV',fontSize=9.1,leading=14.1,textColor=GRAY,spaceAfter=8),
 'small': ParagraphStyle('smallx', fontName='DV',fontSize=8.0,leading=11.4,textColor=GRAY,spaceAfter=6),
 'note': ParagraphStyle('notex', fontName='DV',fontSize=8.2,leading=12.5,textColor=NAVY,spaceAfter=7,
                        borderColor=LINE,borderWidth=.6,borderPadding=10,backColor=LIGHT),
 'h1': ParagraphStyle('h1x', fontName='DV-Bold',fontSize=16.5,leading=21,textColor=NAVY,spaceBefore=16,spaceAfter=10,keepWithNext=True),
 'h2': ParagraphStyle('h2x', fontName='DV-Bold',fontSize=11.7,leading=16,textColor=TEAL,spaceBefore=11,spaceAfter=7,keepWithNext=True),
 'h3': ParagraphStyle('h3x', fontName='DV-Bold',fontSize=9.6,leading=14,textColor=NAVY,spaceBefore=8,spaceAfter=5,keepWithNext=True),
 'table': ParagraphStyle('tablex',fontName='DV',fontSize=7.7,leading=11,textColor=NAVY),
 'table_small': ParagraphStyle('tablesmallx',fontName='DV',fontSize=7.1,leading=10.0,textColor=NAVY),
 'th': ParagraphStyle('thx',fontName='DV-Bold',fontSize=7.8,leading=11,textColor=colors.white),
 'caption': ParagraphStyle('captionx', fontName='DV',fontSize=8,leading=11,textColor=GRAY,alignment=TA_CENTER,spaceAfter=12),
 'coverk': ParagraphStyle('coverk',fontName='DV-Bold',fontSize=10.3,leading=16,textColor=TEAL,alignment=TA_CENTER,spaceAfter=7),
 'covert': ParagraphStyle('covert',fontName='DV-Bold',fontSize=24,leading=31,textColor=NAVY,alignment=TA_CENTER,spaceAfter=16),
 'coversub': ParagraphStyle('coversub',fontName='DV',fontSize=13,leading=19,textColor=GRAY,alignment=TA_CENTER,spaceAfter=20),
 'center': ParagraphStyle('centerx',fontName='DV',fontSize=9.2,leading=16,textColor=NAVY,alignment=TA_CENTER,spaceAfter=8),
}


def P(s,kind='base'):
    return Paragraph(str(s),styles[kind])


def H(story,title,level=1):
    story.append(P(title,'h1' if level==1 else 'h2' if level==2 else 'h3'))


def B(story, text):
    story.append(P(text))


def bullets(story, items):
    for item in items:
        story.append(P('• '+item,'base'))


def table(story, headings, rows, widths, small=False):
    body = [[P(h,'th') for h in headings]]
    kind='table_small' if small else 'table'
    body.extend([[P(str(x),kind) for x in row] for row in rows])
    tb=Table(body,colWidths=widths,repeatRows=1,hAlign='LEFT')
    tb.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, LIGHT]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,0),(-1,0),1.2,TEAL),
        ('LINEBELOW',(0,1),(-1,-1),.32,LINE),
    ]))
    story.append(tb)
    story.append(Spacer(1,11))


def fig(story, basename, caption, width=480):
    from PIL import Image as PILImage
    path=CHARTS/basename
    w,h=PILImage.open(path).size
    story.append(Image(str(path), width=width, height=width*h/w))
    story.append(P(caption,'caption'))


def headerfooter(canvas,doc):
    canvas.saveState()
    w,h=A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(.8)
    canvas.line(43,h-39,w-43,h-39)
    canvas.setFont('DV-Bold',7.5)
    canvas.setFillColor(TEAL)
    canvas.drawString(44,h-31,'TECNM  /  INSTITUTO TECNOLÓGICO SUPERIOR DE MONCLOVA')
    canvas.setStrokeColor(LINE)
    canvas.line(43,42,w-43,42)
    canvas.setFont('DV',7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(43,30,'Unidad 6 · Métodos de búsqueda · Noviembre de 2026')
    canvas.drawRightString(w-43,30,f'Página {doc.page}')
    canvas.restoreState()


def cover(story, task, title, description):
    story.append(Spacer(1,3.3*cm))
    story.append(P('TECNOLÓGICO NACIONAL DE MÉXICO','coverk'))
    story.append(P('INSTITUTO TECNOLÓGICO SUPERIOR DE MONCLOVA','center'))
    story.append(Spacer(1,1.25*cm))
    story.append(P('UNIDAD 6 · MÉTODOS DE BÚSQUEDA','coverk'))
    story.append(P(task,'coversub'))
    story.append(P(title,'covert'))
    story.append(P(description,'coversub'))
    story.append(Spacer(1,1.25*cm))
    story.append(HRFlowable(width='76%', thickness=2, color=TEAL, hAlign='CENTER'))
    story.append(Spacer(1,.7*cm))
    for name, val in [('Estudiante','Aldo Alberto Barajas Ancira'),
                      ('Matrícula','I24050397'),
                      ('Docente','Rubén Riojas'),
                      ('Área','Estructuras de Datos'),
                      ('Fecha','Noviembre de 2026')]:
        story.append(P(f'<b>{name}:</b> {val}','center'))
    story.append(PageBreak())


def build_doc(target, story, title):
    doc=SimpleDocTemplate(str(target),pagesize=A4,
                          leftMargin=46,rightMargin=46,topMargin=55,bottomMargin=57,
                          title=title,author='Aldo Alberto Barajas Ancira',
                          subject='Unidad 6 - Métodos de búsqueda')
    doc.build(story,onFirstPage=headerfooter,onLaterPages=headerfooter)


def source_list(story):
    H(story,'Referencias consultadas',2)
    for i,(autor,tit,url) in enumerate([
        ('NIST, Dictionary of Algorithms and Data Structures','Sequential search','https://xlinux.nist.gov/dads/HTML/sequentialSearch.html'),
        ('CP-Algorithms','Binary search','https://cp-algorithms.com/num_methods/binary_search.html'),
        ('Sedgewick & Wayne, Princeton University','Hash tables (Algorithms, 4th Edition)','https://algs4.cs.princeton.edu/34hash/'),
        ('OpenDSA / Virginia Tech','Open Hashing: separate chaining','https://opendsa-server.cs.vt.edu/ODSA/Books/pubbook/odsa-all/fall-2019/Public_Instance/html/OpenHash.html'),
        ('OpenDSA','Collision Resolution / Open Addressing','https://opendsa-server.cs.vt.edu/ODSA/StandaloneModules/help/20221201151914/html/HashCSimple.html'),
    ],start=1):
        story.append(P(f'[{i}] <b>{autor}</b>. {tit}. <font color="#137C82">{url}</font>','small'))
    story.append(P('Consulta de fuentes: noviembre de 2026. Las complejidades son asintóticas y suponen el modelo de memoria indicado.','small'))


def report_61():
    s=[]
    cover(s,'TAREA 6.1','Cuadro comparativo y análisis de complejidad','Búsqueda secuencial, binaria y por funciones HASH')
    H(s,'1. Planteamiento y propósito')
    B(s,'La búsqueda permite localizar una clave en una colección y responder si existe o recuperar su registro. La elección del método depende de si los datos están ordenados, cuántas consultas se efectuarán, qué memoria adicional es admisible y cómo se distribuyen las claves. El presente análisis contrasta <b>tiempo de consulta, preprocesamiento, memoria y robustez frente a colisiones</b>.')
    B(s,'<b>Notación:</b> n = cantidad de registros; m = cantidad de cubetas de la tabla HASH; α = n/m = factor de carga. O(·) describe una cota asintótica del crecimiento, no un tiempo en segundos. Para HASH se diferencia cuidadosamente entre comportamiento esperado y peor caso.')
    H(s,'2. Funcionamiento de los métodos')
    H(s,'2.1. Búsqueda secuencial',2)
    B(s,'Revisa los elementos desde el primero hasta hallar la clave o llegar al final. Puede aplicarse sobre un arreglo sin orden previo, una lista o un archivo accesible secuencialmente. En el mejor caso la coincidencia está al inicio; en el promedio, si la clave presente se distribuye de forma uniforme, se examinan aproximadamente (n + 1)/2 elementos; en una búsqueda fallida se inspeccionan n.')
    H(s,'2.2. Búsqueda binaria iterativa',2)
    B(s,'Requiere una colección <b>ordenada por la misma clave</b> que se compara. Inspecciona el elemento central y descarta aproximadamente una mitad en cada paso; repite hasta encontrar el objetivo o vaciar el intervalo. No necesita recursión: la versión iterativa solo mantiene índices izquierdo, derecho y medio. Si los datos no están ordenados, el resultado puede ser incorrecto.')
    H(s,'2.3. Búsqueda mediante HASH',2)
    B(s,'Una función de dispersión h(k) transforma la clave k en un índice de cubeta entre 0 y m-1. En la implementación de esta unidad se emplea <b>h(k) = k mod m</b>, con m primo, y cada cubeta almacena una cadena de claves. Las consultas usan primero la función HASH y luego revisan únicamente la cadena correspondiente. El costo esperado depende de la uniformidad de h y del factor de carga, no solo del tamaño n.')
    H(s,'3. Cuadro comparativo analítico')
    table(s,['Método','Mejor caso','Caso promedio','Peor caso','Espacio auxiliar de búsqueda'],[
        ['Secuencial','O(1): primer elemento','O(n): recorrido proporcional a n','O(n): ausente o última posición','O(1)'],
        ['Binaria iterativa','O(1): elemento central','O(log n): intervalos a la mitad','O(log n): hasta agotar intervalo','O(1); recursiva O(log n) por pila'],
        ['HASH con cadenas','O(1): cubeta vacía o primer elemento','O(1 + α) esperado; O(1) si α acotado','O(n): colisiones concentradas en una cubeta','O(1) por consulta; estructura O(n + m)'],
    ],[85,83,120,110,105],small=True)
    s.append(P('<b>Importante:</b> el espacio O(1) de búsqueda es adicional a las estructuras previamente almacenadas. Mantener una copia ordenada para binaria requiere O(n) de almacenamiento adicional; la tabla HASH completa ocupa O(n + m).','note'))
    H(s,'4. Condiciones y costos ocultos')
    table(s,['Aspecto','Secuencial','Binaria','HASH (cadenas)'],[
        ['Orden previo','No','Sí, por clave ascendente','No'],
        ['Preparación','Ninguna obligatoria','Ordenar: O(n log n) típico si los datos llegan desordenados','Construir tabla: O(n) esperado; peor O(n²) con colisiones y verificación de duplicados'],
        ['Inserción / cambios','Sin restaurar orden','Mantener orden puede costar O(n) por inserción en arreglo','O(1 + α) esperado por inserción; redimensionado ocasional'],
        ['Memoria de estructura','Arreglo existente O(n)','Arreglo O(n); copia extra O(n) si se conserva original','Cubetas + entradas: O(n + m)'],
        ['Rangos y orden','Puede recorrerse para recuperar rangos','Muy adecuada para rangos sobre arreglo ordenado','No preserva orden: no conviene para rangos'],
    ],[95,127,137,144],small=True)
    H(s,'5. Funciones HASH: dispersión y colisiones')
    B(s,'<b>Colisión:</b> dos claves distintas obtienen la misma posición base: h(k1) = h(k2). No significa que las claves sean iguales. Por ejemplo, con m = 7, h(3) = h(10) = h(17) = 3. En una tabla real, las colisiones no siempre pueden evitarse y requieren una estrategia explícita [3-5].')
    table(s,['Resolución','Idea principal','Ventajas','Restricciones / riesgo'],[
        ['Encadenamiento separado','Cada cubeta conserva una lista de elementos','Inserción sencilla; admite α > 1','Cadenas largas; referencias y memoria extra'],
        ['Exploración lineal','Probar h(k), h(k)+1, h(k)+2… mod m','Sencillez y buena localidad de memoria','Agrupamiento primario; requiere espacios vacíos'],
        ['Exploración cuadrática','Probar h(k)+i² (según diseño)','Reduce agrupamiento primario','Puede no visitar todas las posiciones; agrupamiento secundario'],
        ['Doble dispersión','Paso de sondeo calculado con segunda función h2(k)','Reduce patrones repetidos de colisión','h2 no puede ser cero; debe permitir recorrer la tabla'],
    ],[94,133,126,150],small=True)
    H(s,'5.1. Ejemplo explicado: tres claves, una cubeta',2)
    B(s,'Usando una capacidad de 7: las claves 3, 10 y 17 tienen residuo 3. Con encadenamiento, la cubeta 3 almacena <b>[3 → 10 → 17]</b>. Buscar 17 requiere examinar tres claves; buscar 24 (ausente, con el mismo residuo) también. Con sondeo lineal, si las posiciones 3, 4 y 5 estaban vacías, las claves se almacenarían respectivamente en 3, 4 y 5. La misma función HASH puede producir distintas secuencias de búsqueda según el método de resolución.')
    B(s,'Una dispersión uniforme y un valor de α controlado ayudan al caso esperado. Si todas las claves caen en una sola cubeta, la tabla con cadenas se comporta como una búsqueda secuencial y degrada a O(n). En entornos expuestos a claves adversarias conviene usar mecanismos robustos de hashing y controlar tamaño y colisiones.')
    H(s,'6. Discusión crítica: ¿cuándo conviene cada método?')
    bullets(s,[
        '<b>Secuencial:</b> útil en colecciones pequeñas, datos sin orden y una sola consulta ocasional. Evita costos de ordenar o crear índices, aunque el tiempo crece linealmente.',
        '<b>Binaria:</b> excelente si la colección ya está ordenada y se ejecutan muchas consultas o búsquedas por rango. Su costo O(log n) no incluye la preparación necesaria para ordenar un conjunto nuevo.',
        '<b>HASH:</b> conveniente para consultas frecuentes de igualdad (IDs, claves y códigos) sin interés por el orden. Gasta más memoria; necesita una buena dispersión y manejo correcto de colisiones.',
        '<b>Decisión por cantidad de consultas:</b> para pocas búsquedas en datos desordenados, preparar estructuras puede costar más que una búsqueda secuencial; para muchas, ordenar una vez o construir un índice HASH suele amortizarse.',
    ])
    H(s,'7. Conclusiones')
    B(s,'No existe un método universalmente superior. La secuencial optimiza simplicidad y ausencia de preparación; la binaria minimiza visitas al operar sobre datos previamente ordenados; HASH puede alcanzar costo esperado cercano a constante en igualdad, pero pierde su ventaja con colisiones severas. La comparación rigurosa debe incorporar <b>tipo de consulta, distribución de entradas, costo de preparación y memoria</b>, además de Big O.')
    source_list(s)
    build_doc(OUT/'Tarea_6_1_Cuadro_Comparativo.pdf',s,'Tarea 6.1 - Cuadro comparativo de búsquedas')


def load_csv(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def report_62():
    s=[]
    resumen=load_csv('resumen.csv')
    prep=load_csv('preparacion.csv')
    cargas=load_csv('cargas_hash.csv')
    colisiones=load_csv('colisiones_forzadas.csv')
    cover(s,'TAREA 6.2','Práctica de programación y evaluación empírica','Implementación reproducible y banco de pruebas de búsquedas')
    H(s,'1. Objetivos y alcance')
    B(s,'Implementar búsqueda secuencial, binaria iterativa y una tabla HASH desde cero; contrastar su corrección, registrar comparaciones e iteraciones y evaluar consultas exitosas y fallidas. El estudio incorpora carga de la tabla, colisiones controladas y tiempo de CPU como métrica complementaria.')
    H(s,'2. Descripción de la implementación')
    table(s,['Método','Implementación','Datos utilizados'],[
        ['Secuencial','Ciclo que inspecciona uno a uno elementos hasta coincidencia o fin.','Arreglo original desordenado.'],
        ['Binaria','Intervalo de índices izquierdo/derecho y punto medio; 1 o 2 comparaciones de clave por paso.','Copia del mismo conjunto ordenada con sorted().'],
        ['HASH','Cubetas con listas; índice h(k)=k mod m; encadenamiento separado, duplicados omitidos.','Mismas claves en tabla propia con m primo y α cercano a 0.75.'],
    ],[98,205,200],small=True)
    B(s,'El proyecto no usa <b>dict</b> ni <b>set</b> para realizar búsquedas HASH. Sí usa herramientas estándar de Python para crear los datos y verificar propiedades; ello no reemplaza los algoritmos implementados.')
    H(s,'3. Diseño del experimento')
    bullets(s,[
        '<b>Tamaños:</b> n = 10,000, 50,000 y 100,000 enteros positivos únicos, seleccionados aleatoriamente del intervalo [1, 10⁹).',
        '<b>Repeticiones independientes:</b> tres semillas fijas (6051, 6052 y 6053) por tamaño, con la semilla combinada con n.',
        '<b>Consultas:</b> 100 claves presentes y 100 ausentes por semilla; las ausentes son negativas y ninguna puede pertenecer al conjunto positivo. En total: 300 consultas exitosas y 300 fallidas por n y método.',
        '<b>Equidad:</b> cada método responde a las mismas claves; las colecciones tienen el mismo contenido, aunque binaria requiere una representación ordenada.',
        '<b>Verificación:</b> se comprueba que toda búsqueda presente devuelve verdadero y toda ausente devuelve falso; pruebas automáticas adicionales cubren vacíos, negativos, duplicados y colisiones.',
    ])
    H(s,'3.1. Definiciones operacionales',2)
    B(s,'Una <b>comparación</b> es una evaluación explícita entre la clave candidata y el objetivo (igualdad == o relación &lt;). Una <b>iteración</b> es una visita a un candidato, ya sea elemento del arreglo o entrada de una cadena. Binaria puede efectuar dos comparaciones en una sola iteración. HASH puede requerir cero comparaciones en una cubeta vacía, pero aun así realiza <b>un acceso a cubeta</b>; este se registra por separado.')
    B(s,'El tiempo de CPU se mide con process_time_ns() por lote de consultas y se divide entre su número. La ordenación previa y la construcción de HASH se cronometran aparte; no se suman al costo de consulta. Los tiempos son observaciones del entorno de ejecución de esta práctica y no garantías de rendimiento en otro equipo.')
    H(s,'4. Resultados principales: comparaciones e iteraciones')
    B(s,'Las cifras siguientes son <b>promedios por consulta</b> agregados de tres semillas, con 300 consultas por condición y tamaño en cada técnica. Los CSV conservan tanto los totales como las observaciones individuales.')
    for condicion in ('Exitosa','Fallida'):
        H(s,'4.'+('1' if condicion=='Exitosa' else '2')+'. Consultas '+condicion.lower(),2)
        rows=[]
        for n in (10000,50000,100000):
            for metodo in ('Secuencial','Binaria','Hash encadenada'):
                r=next(row for row in resumen if int(row['N'])==n and row['metodo']==metodo and row['resultado']==condicion)
                rows.append([f'{n:,}',metodo,
                             f"{float(r['comparaciones_promedio']):,.2f}",
                             f"{float(r['iteraciones_promedio']):,.2f}",
                             f"{float(r['accesos_cubeta_promedio']):,.2f}",
                             f"{float(r['cpu_medio_por_consulta_us']):,.2f}"])
        table(s,['N','Algoritmo','Comparac.','Iteraciones','Accesos<br/>cubeta','CPU/consulta<br/>(µs)'],rows,[61,123,87,85,69,78],small=True)
    s.append(P('<b>Interpretación:</b> el número de comparaciones de HASH puede ser inferior a 1 en búsquedas fallidas porque muchas cubetas están vacías. Esto <b>no</b> significa que una consulta HASH carezca de costo: la dispersión y el acceso a la cubeta siguen ocurriendo. En binaria, las comparaciones superan a las iteraciones porque el código distingue igualdad y orden.','note'))
    H(s,'5. Gráficas comparativas')
    fig(s,'comparaciones_exitosa.png','Figura 1. Comparaciones por consulta exitosa; eje vertical con escala simétrica logarítmica.',width=430)
    fig(s,'comparaciones_fallida.png','Figura 2. Comparaciones por consulta fallida; cifras exactas en las tablas de la sección 4.',width=430)
    fig(s,'iteraciones_exitosa.png','Figura 3. Iteraciones en búsquedas exitosas para los tres tamaños.',width=430)
    fig(s,'iteraciones_fallida.png','Figura 4. Iteraciones en búsquedas fallidas para los tres tamaños.',width=430)
    fig(s,'tiempo_cpu_exitosa.png','Figura 5. Tiempo de CPU promedio en búsquedas exitosas; no incluye preprocesamiento.',width=430)
    fig(s,'tiempo_cpu_fallida.png','Figura 6. Tiempo de CPU promedio en búsquedas fallidas; dependiente del entorno.',width=430)
    H(s,'6. Costo de preparar las estructuras')
    tabla_pre=[]
    for n in (10000,50000,100000):
        rs=[r for r in prep if int(r['N'])==n]
        tabla_pre.append([f'{n:,}',f"{mean(float(r['ordenacion_cpu_ms']) for r in rs):,.2f}",
                          f"{mean(float(r['hash_construccion_cpu_ms']) for r in rs):,.2f}",
                          f"{int(rs[0]['capacidad_hash']):,}",
                          f"{mean(float(r['colisiones_insercion']) for r in rs):,.0f}",
                          f"{max(int(r['max_cadena']) for r in rs)}"])
    table(s,['N','Ordenar<br/>CPU ms','Crear HASH<br/>CPU ms','Cubetas HASH','Colisiones inserción<br/>(prom.)','Cadena máx.'],tabla_pre,
          [67,76,92,94,103,71],small=True)
    B(s,'El tiempo de construcción HASH incluye reservar cubetas, insertar claves y verificar duplicados por cadena (no incluye calcular la capacidad); el tiempo de ordenación corresponde a sorted(datos). La elección para una sola búsqueda podría diferir de la elección para miles de consultas, pues la preparación no es gratuita.')
    H(s,'7. Colisiones y factor de carga')
    B(s,'Se mantuvieron 50,000 claves y se varió m para evaluar α = n/m. Las entradas son iguales en todos los ensayos; se realizaron 200 consultas presentes y 200 ausentes por nivel de carga. A diferencia del sondeo abierto, <b>el encadenamiento separado admite α mayor que 1</b>.')
    rows=[]
    for r in cargas:
        rows.append([r['carga_objetivo'],r['carga_real'],r['condicion'],r['comparaciones_promedio'],
                     r['colisiones_insercion'],r['max_cadena']])
    table(s,['Carga<br/>objetivo','α real','Consulta','Comparac.<br/>promedio','Colisiones<br/>insertadas','Cadena<br/>máx.'], rows,[73,75,81,92,103,79],small=True)
    fig(s,'hash_factor_carga.png','Figura 7. Con más carga y claves distribuidas aleatoriamente, las cadenas tienden a alargarse.',width=430)
    H(s,'7.1. Ensayo patológico reproducible',2)
    B(s,'Se introdujeron 500 claves distintas de la forma <b>7 + i × 1009</b> (i de 0 a 499) en una tabla de 1009 cubetas. Todas tienen índice HASH 7. Así se construyó intencionalmente una cadena de longitud 500 que demuestra el peor caso.')
    table(s,['Consulta','Índice','¿Existe?','Comparaciones','Iteraciones'],[
        [r['caso'],r['h_clave'], 'Sí' if r['encontrado']=='True' else 'No',r['comparaciones'],r['iteraciones']] for r in colisiones
    ],[192,60,60,96,95],small=True)
    H(s,'8. Discusión de los resultados')
    n100={ (r['metodo'],r['resultado']):r for r in resumen if r['N']=='100000'}
    B(s,f'Con n = 100,000, las búsquedas fallidas registraron <b>{float(n100[("Secuencial","Fallida")]["comparaciones_promedio"]):,.0f}</b> comparaciones secuenciales frente a <b>{float(n100[("Binaria","Fallida")]["comparaciones_promedio"]):,.0f}</b> en binaria y <b>{float(n100[("Hash encadenada","Fallida")]["comparaciones_promedio"]):.2f}</b> en HASH. La búsqueda secuencial examina todo el conjunto para confirmar la ausencia, mientras que la binaria descarta mitades y HASH revisa una sola cubeta, aunque debe primero construir su índice.')
    B(s,'En búsquedas exitosas, la posición de la clave determina cuántos elementos recorre la secuencial. La binaria tiene un crecimiento lento, compatible con O(log n). HASH conserva pocas visitas con carga limitada y dispersión razonablemente uniforme, pero el caso forzado exhibe 500 comparaciones en una sola cubeta, confirmando que su peor caso no es O(1).')
    H(s,'8.1. Limitaciones y validez',2)
    bullets(s,[
        'Los datos y consultas son aleatorios reproducibles, pero no representan todos los patrones reales ni claves intencionalmente maliciosas. Se añadió por separado un escenario de colisiones forzadas.',
        'Las mediciones de CPU en Python son sensibles al intérprete, sistema operativo, procesador y ejecución concurrente. Las comparaciones e iteraciones son más transportables para análisis algorítmico.',
        'La búsqueda secuencial usa una lista sin ordenar; binaria utiliza copia ordenada; HASH necesita reservar y construir su tabla. No se interpretan los tiempos de consulta como un costo total de extremo a extremo.',
        'La función modular h(k)=k mod m se usa con fines didácticos; no es una política de seguridad ante entradas adversarias ni sustituye un diseño HASH robusto para producción.',
    ])
    H(s,'9. Conclusiones empíricas')
    B(s,'El experimento respalda el patrón teórico: secuencial crece aproximadamente de forma lineal, binaria realiza unas pocas decenas de comparaciones incluso con 100,000 registros y HASH suele examinar pocas claves mientras las colisiones estén distribuidas. Sin embargo, HASH demanda memoria y preparación; el caso adversarial muestra que su eficacia depende crucialmente de la función de dispersión y de cómo se resuelven las colisiones. Para una solución real deben valorarse cantidad de consultas, frecuencia de actualización, necesidad de orden y patrón de claves.')
    H(s,'10. Instrucciones de reproducción')
    for cmd in ['python codigo/demo_interactiva.py',
                'python -m unittest discover -s codigo -p "prueba_*.py" -v',
                'python codigo/experimento.py --salida datos',
                'python codigo/generar_graficas.py --datos datos --salida graficas']:
        s.append(P('<font color="#1F5F7B">'+cmd+'</font>','small'))
    B(s,'Las primeras tres órdenes funcionan con Python 3.10+ y biblioteca estándar. Para regenerar las gráficas se necesita instalar matplotlib. Los CSV incluyen datos por semilla, resumen, preparación, estudio de cargas y colisiones forzadas.')
    source_list(s)
    build_doc(OUT/'Tarea_6_2_Reporte_Practica.pdf',s,'Tarea 6.2 - Práctica empírica de búsquedas')


if __name__=='__main__':
    report_61()
    report_62()
    for p in OUT.glob('*.pdf'):
        print(p,round(p.stat().st_size/1024),'KiB')
