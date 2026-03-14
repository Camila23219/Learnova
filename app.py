#Se importo la herramienta de flask para crear la página
#El render template muestra los archivos html
#Y request recibe los datos del formulario
from flask import Flask, render_template, request
import sqlite3
# Creamos la aplicación web
# __name__ le dice a Flask dónde está el programa principal
app = Flask(__name__)
def crear_db():
    conn = sqlite3.connect("respuestas.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respuestas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        p1 TEXT,
        p2 TEXT,
        p3 TEXT,
        p4 TEXT,
        p5 TEXT,
        p6 TEXT,
        p7 TEXT,
        p8 TEXT,
        p9 TEXT,
        p10 TEXT,
        p11 TEXT,
        p12 TEXT
    )
    """)

    conn.commit()
    conn.close()

crear_db()
#Aqui entra la ruta principal que se ejecuta cuando el usuario entra a 
#http://127.0.0.1:5000/
@app.route('/')
def encuesta():
    # render_template busca el archivo dentro de la carpeta:
    # templates/encuesta.html
    # y lo muestra en el navegador
    return render_template('encuesta.html')

#Esta ruta recibe las respuestas del formulario
#y se activa cuando el formulario es enviado
@app.route('/resultado', methods=['POST'])
def resultado():

    visual = 0
    auditivo = 0
    kinestesico = 0

    tema = request.form['tema']
    respuestas = []

    for i in range(1,13):
        respuesta = request.form[f"p{i}"]
        respuestas.append(respuesta)

        if respuesta == "visual":
            visual += 1
        elif respuesta == "auditivo":
            auditivo += 1
        elif respuesta == "kinestesico":
            kinestesico += 1

    # GUARDAR RESPUESTAS EN LA BASE DE DATOS
    conn = sqlite3.connect("respuestas.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO respuestas
    (tema,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (tema, *respuestas))

    conn.commit()
    conn.close()
#Aqui se determina que tipo de aprendizaje eres comparando las respuestas
#Depende del resultado se recomienda tipos de aprendizaje 
    if visual > auditivo and visual > kinestesico:
        estilo = "Visual"
        recurso = f"https://www.youtube.com/results?search_query={tema}+explicacion+visual"

        metodos = """
        <ul>
        <li>Usar mapas mentales</li>
        <li>Ver videos educativos</li>
        <li>Estudiar con diagramas e infografías</li>
        <li>Subrayar con colores</li>
        </ul>
        """

    elif auditivo > visual and auditivo > kinestesico:
        estilo = "Auditivo"
        recurso = f"https://www.youtube.com/results?search_query={tema}+explicacion"

        metodos = """
        <ul>
        <li>Escuchar podcasts o explicaciones</li>
        <li>Leer en voz alta</li>
        <li>Explicar el tema a otra persona</li>
        <li>Grabar tu voz explicando el tema</li>
        </ul>
        """

    else:
        estilo = "Kinestésico"
        recurso = f"https://www.google.com/search?q=ejercicios+{tema}"

        metodos = """
        <ul>
        <li>Hacer ejercicios prácticos</li>
        <li>Aprender con experimentos</li>
        <li>Usar juegos educativos</li>
        <li>Aprender haciendo proyectos</li>
        </ul>
        """
# Aquí se devuelve una página HTML completa
# usando un f-string para insertar variables
#python lo reemplaza por valores reales
#Hay otra página para cuando se arrojan los resultados
#Se hizo para personalizarla acorde a la pagina de la encuesta
    return f"""
    <!DOCTYPE html>
<html>

<head>
<meta charset="UTF-8">
<title>Resultado Learnova</title>

<style>

body{{
font-family: Arial;
background:#e0eba4;
text-align:center;
padding:40px;
}}

.tarjeta{{
background:white;
width:500px;
margin:auto;
padding:30px;
border-radius:10px;
box-shadow:0 4px 10px rgba(0,0,0,0.2);
}}

h2{{
color:#3768a0;
}}

button{{
background:#3768a0;
color:white;
border:none;
padding:10px 20px;
border-radius:6px;
font-size:16px;
cursor:pointer;
}}

button:hover{{
background:#2c5685;
}}

</style>

</head>

<body>

<div class="tarjeta">

<h2>Resultado del Test</h2>

<p>Tema que quieres aprender: <b>{tema}</b></p>

<p>Visual: {visual}</p>
<p>Auditivo: {auditivo}</p>
<p>Kinestésico: {kinestesico}</p>

<h3>Tu estilo de aprendizaje es:</h3>

<h2>{estilo}</h2>

<h3>Métodos de estudio recomendados:</h3>

{metodos}

<br>

<a href="{recurso}" target="_blank">
<button>Buscar recursos para aprender {tema}</button>
</a>

<br><br>

<a href="/">
<button>Volver al test</button>
</a>

</div>

</body>
</html>
"""

app.run(debug=True)