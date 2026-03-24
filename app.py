from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'learnova_2026_secret'

DASHBOARD_PASSWORD = 'admin123'

# En Vercel el filesystem es de solo lectura, se usa /tmp para la BD
DB_PATH = '/tmp/respuestas.db' if os.environ.get('VERCEL') else 'respuestas.db'

def crear_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respuestas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        p1 TEXT, p2 TEXT, p3 TEXT, p4 TEXT,
        p5 TEXT, p6 TEXT, p7 TEXT, p8 TEXT,
        p9 TEXT, p10 TEXT, p11 TEXT, p12 TEXT
    )
    """)
    conn.commit()
    conn.close()

crear_db()

@app.route('/')
def encuesta():
    return render_template('encuesta.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    visual = 0
    auditivo = 0
    kinestesico = 0

    tema = request.form['tema']
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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO respuestas (tema,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (tema, *respuestas))
    conn.commit()
    conn.close()

    if visual > auditivo and visual > kinestesico:
        estilo = "Visual"
        icono = "👁️"
        recurso = f"https://www.youtube.com/results?search_query={tema}+explicacion+visual"
        metodos = [
            ("🗺️", "Mapas mentales", "Organiza ideas visualmente"),
            ("🎬", "Videos educativos", "Aprende viendo explicaciones"),
            ("📊", "Diagramas e infografías", "Convierte info en imágenes"),
            ("🖊️", "Subrayar con colores", "Destaca lo más importante"),
        ]
    elif auditivo > visual and auditivo > kinestesico:
        estilo = "Auditivo"
        icono = "👂"
        recurso = f"https://www.youtube.com/results?search_query={tema}+explicacion"
        metodos = [
            ("🎙️", "Podcasts y audios", "Escucha contenido educativo"),
            ("📢", "Leer en voz alta", "Activa tu memoria auditiva"),
            ("👥", "Explicar a otros", "Enseña y aprenderás más"),
            ("🎤", "Grabar tu voz", "Repasa escuchándote a ti mismo"),
        ]
    else:
        estilo = "Kinestésico"
        icono = "✋"
        recurso = f"https://www.google.com/search?q=ejercicios+practicos+{tema}"
        metodos = [
            ("🧪", "Ejercicios prácticos", "Aprende haciendo"),
            ("🔬", "Experimentos", "Explora con tus manos"),
            ("🎮", "Juegos educativos", "Gamifica tu aprendizaje"),
            ("🛠️", "Proyectos", "Construye para entender"),
        ]

    return render_template('resultado.html',
        tema=tema,
        estilo=estilo,
        icono=icono,
        visual=visual,
        auditivo=auditivo,
        kinestesico=kinestesico,
        metodos=metodos,
        recurso=recurso
    )

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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM respuestas")
    total = cursor.fetchone()[0]

    if total == 0:
        conn.close()
        return render_template('dashboard.html', total=0, estilos={}, temas=[], recientes=[])

    # Distribucion de estilos
    cursor.execute("SELECT p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12 FROM respuestas")
    estilos_count = {'visual': 0, 'auditivo': 0, 'kinestesico': 0}
    for row in cursor.fetchall():
        estilo = calcular_estilo_fila(row)
        estilos_count[estilo] += 1
    estilos = {k: v for k, v in estilos_count.items() if v > 0}

    # Top 5 temas
    cursor.execute("SELECT tema, COUNT(*) as cnt FROM respuestas GROUP BY tema ORDER BY cnt DESC LIMIT 5")
    temas = [{"tema": r[0], "count": r[1]} for r in cursor.fetchall()]

    # Ultimas 5 respuestas
    cursor.execute("SELECT id, tema, p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12 FROM respuestas ORDER BY id DESC LIMIT 5")
    recientes = []
    for row in cursor.fetchall():
        recientes.append({
            'id': row[0],
            'tema': row[1],
            'estilo': calcular_estilo_fila(row[2:])
        })

    conn.close()

    return render_template('dashboard.html',
        total=total,
        estilos=estilos,
        temas=temas,
        recientes=recientes
    )

if __name__ == '__main__':
    app.run(debug=True)
