from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = 'learnova_2026_secret'

DASHBOARD_PASSWORD = 'admin123'

def crear_db():
    conn = sqlite3.connect("respuestas.db")
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

    conn = sqlite3.connect("respuestas.db")
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

@app.route('/dashboard')
def dashboard():
    if not session.get('dashboard_auth'):
        return redirect(url_for('dashboard_login'))
    conn = sqlite3.connect("respuestas.db")
    df = pd.read_sql_query("SELECT * FROM respuestas", conn)
    conn.close()

    total = len(df)

    if total == 0:
        return render_template('dashboard.html', total=0, estilos={}, temas=[], recientes=[])

    cols = [f'p{i}' for i in range(1, 13)]

    def calcular_estilo(row):
        conteo = row[cols].value_counts()
        return conteo.idxmax()

    df['estilo'] = df.apply(calcular_estilo, axis=1)

    estilos = df['estilo'].value_counts().to_dict()
    temas_top = df['tema'].value_counts().head(5)
    temas = [{"tema": t, "count": int(c)} for t, c in temas_top.items()]
    recientes = df.tail(5)[['id', 'tema', 'estilo']].iloc[::-1].to_dict('records')

    return render_template('dashboard.html',
        total=total,
        estilos=estilos,
        temas=temas,
        recientes=recientes
    )

app.run(debug=True)
