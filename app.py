from flask import Flask, render_template, request, session, redirect, url_for, Response
import psycopg2
import os
import csv
import io
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = 'learnova_2026_secret'

DASHBOARD_PASSWORD = 'admin123'

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def crear_db():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP DEFAULT NOW(),
            tema TEXT,
            p1 TEXT, p2 TEXT, p3 TEXT, p4 TEXT,
            p5 TEXT, p6 TEXT, p7 TEXT, p8 TEXT,
            p9 TEXT, p10 TEXT, p11 TEXT, p12 TEXT
        )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error al inicializar: {e}")

crear_db()

# ---------- RUTAS PRINCIPALES ----------

@app.route('/')
def landing():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM respuestas")
        total = cursor.fetchone()[0]
        conn.close()
    except:
        total = 0
    return render_template('landing.html', total=total)

@app.route('/encuesta')
def encuesta():
    return render_template('encuesta.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    visual = 0
    auditivo = 0
    kinestesico = 0

    tema = request.form['tema']
    tema_url = tema.replace(' ', '+')
    respuestas = []

    for i in range(1, 13):
        respuesta = request.form[f"p{i}"]
        respuestas.append(respuesta)
        if respuesta == "visual":
            visual += 1
        elif respuesta == "auditivo":
            auditivo += 1
        elif respuesta == "kinestesico":
            kinestesico += 1

    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO respuestas (tema,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (tema, *respuestas))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error al guardar: {e}")

    if visual > auditivo and visual > kinestesico:
        estilo = "Visual"
        icono = "👁️"
        metodos = [
            ("🗺️", "Mapas mentales", "Organiza ideas visualmente"),
            ("🎬", "Videos educativos", "Aprende viendo explicaciones"),
            ("📊", "Diagramas e infografías", "Convierte info en imágenes"),
            ("🖊️", "Subrayar con colores", "Destaca lo más importante"),
        ]
        plan = [
            f"Ver un video introductorio sobre {tema} en YouTube",
            "Crear un mapa mental con los conceptos principales",
            f"Buscar infografías o diagramas que resuman {tema}",
            "Subrayar y colorear tus apuntes por categorías",
        ]
        recursos = [
            {"icono": "▶️", "nombre": "YouTube", "desc": "Videos visuales", "color": "#FF0000",
             "url": f"https://www.youtube.com/results?search_query={tema_url}+explicacion+visual"},
            {"icono": "📚", "nombre": "Khan Academy", "desc": "Lecciones con diagramas", "color": "#14BF96",
             "url": f"https://www.khanacademy.org/search?page_search_query={tema_url}"},
            {"icono": "📖", "nombre": "Wikipedia", "desc": "Referencia con imágenes", "color": "#3366CC",
             "url": f"https://es.wikipedia.org/w/index.php?search={tema_url}"},
        ]
    elif auditivo > visual and auditivo > kinestesico:
        estilo = "Auditivo"
        icono = "👂"
        metodos = [
            ("🎙️", "Podcasts y audios", "Escucha contenido educativo"),
            ("📢", "Leer en voz alta", "Activa tu memoria auditiva"),
            ("👥", "Explicar a otros", "Enseña y aprenderás más"),
            ("🎤", "Grabar tu voz", "Repasa escuchándote a ti mismo"),
        ]
        plan = [
            f"Escuchar una explicación en YouTube sobre {tema}",
            "Leer el tema en voz alta o grabarte explicándolo",
            f"Buscar un podcast o audio educativo sobre {tema}",
            "Explicarle el tema a alguien más con tus propias palabras",
        ]
        recursos = [
            {"icono": "▶️", "nombre": "YouTube", "desc": "Explicaciones en audio/video", "color": "#FF0000",
             "url": f"https://www.youtube.com/results?search_query={tema_url}+explicacion"},
            {"icono": "📚", "nombre": "Khan Academy", "desc": "Lecciones paso a paso", "color": "#14BF96",
             "url": f"https://www.khanacademy.org/search?page_search_query={tema_url}"},
            {"icono": "📖", "nombre": "Wikipedia", "desc": "Resumen del tema", "color": "#3366CC",
             "url": f"https://es.wikipedia.org/w/index.php?search={tema_url}"},
        ]
    else:
        estilo = "Kinestésico"
        icono = "✋"
        metodos = [
            ("🧪", "Ejercicios prácticos", "Aprende haciendo"),
            ("🔬", "Experimentos", "Explora con tus manos"),
            ("🎮", "Juegos educativos", "Gamifica tu aprendizaje"),
            ("🛠️", "Proyectos", "Construye para entender"),
        ]
        plan = [
            f"Buscar ejercicios prácticos sobre {tema} en Khan Academy",
            f"Intentar resolver un problema o actividad de {tema}",
            "Crear un pequeño proyecto aplicando lo que aprendiste",
            f"Buscar experimentos o simulaciones de {tema} en YouTube",
        ]
        recursos = [
            {"icono": "▶️", "nombre": "YouTube", "desc": "Tutoriales y experimentos", "color": "#FF0000",
             "url": f"https://www.youtube.com/results?search_query={tema_url}+ejercicios+practicos"},
            {"icono": "📚", "nombre": "Khan Academy", "desc": "Ejercicios interactivos", "color": "#14BF96",
             "url": f"https://www.khanacademy.org/search?page_search_query={tema_url}"},
            {"icono": "📖", "nombre": "Wikipedia", "desc": "Contexto del tema", "color": "#3366CC",
             "url": f"https://es.wikipedia.org/w/index.php?search={tema_url}"},
        ]

    return render_template('resultado.html',
        tema=tema, estilo=estilo, icono=icono,
        visual=visual, auditivo=auditivo, kinestesico=kinestesico,
        metodos=metodos, plan=plan, recursos=recursos
    )

# ---------- DASHBOARD ----------

@app.route('/dashboard/login', methods=['GET', 'POST'])
def dashboard_login():
    error = None
    if request.method == 'POST':
        if request.form['clave'] == DASHBOARD_PASSWORD:
            session['dashboard_auth'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Clave incorrecta. Intenta de nuevo.'
    return render_template('login.html', error=error)

@app.route('/dashboard/logout')
def dashboard_logout():
    session.pop('dashboard_auth', None)
    return redirect(url_for('dashboard_login'))

def calcular_estilo_fila(valores):
    conteo = {'visual': 0, 'auditivo': 0, 'kinestesico': 0}
    for v in valores:
        if v in conteo:
            conteo[v] += 1
    return max(conteo, key=conteo.get)

@app.route('/dashboard')
def dashboard():
    if not session.get('dashboard_auth'):
        return redirect(url_for('dashboard_login'))

    periodo = request.args.get('periodo', 'todo')

    if periodo == 'hoy':
        fecha_filter = "WHERE fecha::date = CURRENT_DATE"
    elif periodo == 'semana':
        fecha_filter = "WHERE fecha >= NOW() - INTERVAL '7 days'"
    else:
        fecha_filter = ""

    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM respuestas {fecha_filter}")
        total = cursor.fetchone()[0]

        if total == 0:
            conn.close()
            return render_template('dashboard.html', total=0, estilos={}, temas=[], recientes=[], periodo=periodo)

        cursor.execute(f"SELECT p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12 FROM respuestas {fecha_filter}")
        estilos_count = {'visual': 0, 'auditivo': 0, 'kinestesico': 0}
        for row in cursor.fetchall():
            estilos_count[calcular_estilo_fila(row)] += 1
        estilos = {k: v for k, v in estilos_count.items() if v > 0}

        cursor.execute(f"SELECT tema, COUNT(*) as cnt FROM respuestas {fecha_filter} GROUP BY tema ORDER BY cnt DESC LIMIT 5")
        temas = [{"tema": r[0], "count": r[1]} for r in cursor.fetchall()]

        cursor.execute(f"SELECT id, fecha, tema, p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12 FROM respuestas {fecha_filter} ORDER BY id DESC LIMIT 5")
        recientes = []
        for row in cursor.fetchall():
            recientes.append({
                'id': row[0],
                'fecha': str(row[1])[:16] if row[1] else '—',
                'tema': row[2],
                'estilo': calcular_estilo_fila(row[3:])
            })

        conn.close()
    except Exception as e:
        print(f"[DB] Error en dashboard: {e}")
        return render_template('dashboard.html', total=0, estilos={}, temas=[], recientes=[], periodo=periodo)

    return render_template('dashboard.html',
        total=total, estilos=estilos, temas=temas,
        recientes=recientes, periodo=periodo
    )

@app.route('/dashboard/export')
def export_csv():
    if not session.get('dashboard_auth'):
        return redirect(url_for('dashboard_login'))
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, tema, p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12 FROM respuestas ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"Error: {e}", 500

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID','Fecha','Tema','P1','P2','P3','P4','P5','P6','P7','P8','P9','P10','P11','P12','Estilo'])
    for row in rows:
        writer.writerow(list(row) + [calcular_estilo_fila(row[3:])])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=learnova_datos.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)
