import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SIMCE Parral - Tierra de Neruda", page_icon="📝", layout="wide")

# Frases motivacionales de Neruda y Parral
FRASES_MOTIVACIONALES = [
    "“El niño que no juega no es niño, pero el hombre que no juega perdió para siempre al niño que vivía en él.” - Pablo Neruda",
    "“Queda prohibido no sonreír a los problemas, no luchar por lo que quieres, abandonarlo todo por miedo.” - Neruda",
    "“Si nada nos salva de la muerte, al menos que el amor nos salve de la vida.” - Neruda",
    "¡Sigue adelante, Parralino! Tu esfuerzo es la semilla de tu futuro.",
    "Como las parras de nuestra tierra, tú también crecerás fuerte y darás frutos."
]

# Estilos CSS con alto contraste y diseño premium para niños
st.markdown("""
    <style>
    /* Estilo General */
    .main {
        background-color: #ffffff;
    }
    
    /* Contenedores de Tarjetas con Alto Contraste */
    .pregunta-card {
        background-color: #f0f7ff;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 2px solid #0056b3;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #000000; /* Texto Negro para máximo contraste */
    }
    
    .pregunta-card b {
        color: #004085;
        font-size: 1.2em;
    }

    .texto-lectura {
        background-color: #fffdf0;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        font-family: 'Georgia', serif;
        font-size: 1.25em;
        line-height: 1.7;
        color: #1a1a1a;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    /* Botones Premium */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(135deg, #28a745, #1e7e34); /* Verde Parral */
        color: white;
        font-weight: bold;
        font-size: 1.1em;
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(40, 167, 69, 0.4);
        background: linear-gradient(135deg, #218838, #19692c);
    }

    /* Medallas y Títulos */
    .medal-container {
        text-align: center;
        padding: 20px;
        border-radius: 20px;
        background: #f8f9fa;
        border: 3px dashed #ffc107;
    }
    
    .neruda-quote {
        font-style: italic;
        color: #5a5a5a;
        text-align: center;
        padding: 20px;
        background-color: #e9ecef;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #0056b3;
    }
    
    /* Forzar visibilidad de Radio Buttons en modo oscuro si el usuario lo tiene activo */
    .stRadio label {
        color: #000000 !important;
        font-weight: 500;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
DB_PATH = "simce_app/datos/resultados.db"

def init_db():
    if not os.path.exists("simce_app/datos"):
        os.makedirs("simce_app/datos")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    codigo_curso TEXT,
                    puntaje_mat INTEGER,
                    correctas_mat INTEGER,
                    puntaje_len INTEGER,
                    correctas_len INTEGER,
                    fecha TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def save_result(nombre, codigo, p_mat, c_mat, p_len, c_len):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO resultados (nombre, codigo_curso, puntaje_mat, correctas_mat, puntaje_len, correctas_len, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (nombre, codigo, p_mat, c_mat, p_len, c_len, datetime.now()))
    conn.commit()
    conn.close()

# --- LÓGICA DE PUNTAJE SIMCE (200-400) ---
def calcular_puntaje_simce(correctas, total):
    if total == 0: return 200
    porcentaje = correctas / total
    return int(200 + (porcentaje * 200))

def obtener_medalla(puntaje):
    if puntaje >= 350: return "🥇 Oro - ¡Excelente Trabajo!", "🏆"
    if puntaje >= 300: return "🥈 Plata - ¡Muy Bien!", "⭐"
    if puntaje >= 250: return "🥉 Bronce - ¡Buen Esfuerzo!", "👍"
    return "🥉 Mención - ¡Sigue Practicando!", "📖"

# --- CONTENIDO --- (Se mantienen las preguntas previas)
PREGUNTAS_MAT = [
    {"q": "¿Cuánto es 125 + 347?", "options": ["462", "472", "482", "452"], "a": "472"},
    {"q": "Si tengo 4 bolsas con 15 manzanas cada una, ¿cuántas manzanas tengo en total?", "options": ["45", "50", "60", "65"], "a": "60"},
    {"q": "¿Cuál es el resultado de 100 - 37?", "options": ["63", "73", "53", "67"], "a": "63"},
    {"q": "¿Qué número es mayor?", "options": ["0.5", "0.25", "0.75", "0.1"], "a": "0.75"},
    {"q": "¿Cuántos minutos hay en 3 horas?", "options": ["120", "150", "180", "200"], "a": "180"},
    {"q": "¿Cuál es el valor de 'x' en 2x + 5 = 15?", "options": ["10", "5", "7", "3"], "a": "5"},
    {"q": "Un triángulo tiene lados de 3cm, 4cm y 5cm. ¿Cómo se clasifica según sus ángulos?", "options": ["Acutángulo", "Obtusángulo", "Rectángulo", "Equilátero"], "a": "Rectángulo"},
    {"q": "¿Cuál es el 25% de 200?", "options": ["25", "50", "75", "100"], "a": "50"},
    {"q": "Si un litro de leche cuesta $900, ¿cuánto cuestan 5 litros?", "options": ["$4.000", "$4.500", "$5.000", "$3.500"], "a": "$4.500"},
    {"q": "¿Cuál es el área de un cuadrado de lado 6cm?", "options": ["12 cm²", "24 cm²", "36 cm²", "18 cm²"], "a": "36 cm²"},
    {"q": "El número 4.567 redondeado a la centena más cercana es:", "options": ["4.500", "4.600", "4.570", "4.000"], "a": "4.600"},
    {"q": "¿Cuántos gramos hay en 2,5 kilogramos?", "options": ["250 g", "2.500 g", "25.000 g", "25 g"], "a": "2.500 g"},
    {"q": "¿Cuál es el resultado de 8 x 7?", "options": ["54", "56", "64", "48"], "a": "56"},
    {"q": "Si repartes 24 caramelos entre 6 niños, ¿cuántos recibe cada uno?", "options": ["3", "4", "5", "6"], "a": "4"},
    {"q": "Un ángulo de 90 grados es un ángulo:", "options": ["Agudo", "Obtuso", "Recto", "Llano"], "a": "Recto"},
    {"q": "Si hoy es martes, ¿qué día será en 10 días más?", "options": ["Viernes", "Sábado", "Domingo", "Jueves"], "a": "Viernes"},
    {"q": "¿Cuál es el sucesor de 9.999?", "options": ["10.000", "9.998", "10.001", "11.000"], "a": "10.000"},
    {"q": "¿A qué hora marca un reloj si el minutero está en el 6 y la hora en el 3?", "options": ["3:06", "6:03", "3:30", "6:30"], "a": "3:30"},
    {"q": "¿Cuántos centímetros hay en 1,5 metros?", "options": ["15 cm", "150 cm", "1.500 cm", "105 cm"], "a": "150 cm"},
    {"q": "Si una pizza se divide en 8 partes y me como 3, ¿qué fracción queda?", "options": ["3/8", "5/8", "1/8", "8/3"], "a": "5/8"},
    {"q": "¿Cuál es el doble de 1.500?", "options": ["3.000", "2.500", "4.500", "2.000"], "a": "3.000"},
    {"q": "La mitad de 500 es:", "options": ["200", "250", "300", "150"], "a": "250"},
    {"q": "¿Cuál es el número romano para 10?", "options": ["V", "X", "L", "C"], "a": "X"},
    {"q": "¿Cuál es el perímetro de un rectángulo de 5cm de largo y 3cm de ancho?", "options": ["8 cm", "15 cm", "16 cm", "10 cm"], "a": "16 cm"},
    {"q": "Si un tren sale a las 14:00 y llega a las 16:30, ¿cuánto duró el viaje?", "options": ["1 hora", "2 horas", "2 horas y media", "3 horas"], "a": "2 horas y media"},
    {"q": "En el número 5.678, ¿qué valor tiene el dígito 6?", "options": ["6", "60", "600", "6.000"], "a": "600"},
    {"q": "¿Cuál es el resultado de 15 dividido por 3?", "options": ["3", "4", "5", "6"], "a": "5"},
    {"q": "¿Qué figura tiene 5 lados?", "options": ["Hexágono", "Pentágono", "Cuadrado", "Triángulo"], "a": "Pentágono"},
    {"q": "Si tengo 3 monedas de $500 y 4 de $100, ¿cuánto dinero tengo?", "options": ["$1.500", "$1.900", "$2.000", "$1.400"], "a": "$1.900"},
    {"q": "¿Cuál es el producto de 9 x 9?", "options": ["18", "72", "81", "90"], "a": "81"}
]

TEXTOS_LEN = [
    {
        "titulo": "El Zorro y la Cigüeña",
        "texto": "Un día, el zorro invitó a la cigüeña a cenar. Para burlarse de ella, le sirvió una sopa en un plato muy llano. La cigüeña, con su largo pico, no pudo probar ni una gota. Al día siguiente, la cigüeña invitó al zorro y sirvió la comida en un jarro largo y estrecho.",
        "questions": [
            {"q": "¿Por qué el zorro usó un plato llano?", "options": ["Para ayudar", "Para burlarse", "Por error", "Era su único plato"], "a": "Para burlarse"},
            {"q": "¿Cómo se vengó la cigüeña?", "options": ["No lo invitó", "Usó un jarro largo", "Le gritó", "Le dio mucha sopa"], "a": "Usó un jarro largo"}
        ]
    },
    {
        "titulo": "La Montaña Mágica",
        "texto": "En lo alto de la montaña vivía un gigante que guardaba un tesoro de nubes. Quien subiera sin zapatos podría pedir un deseo. Pedro lo intentó un martes de verano.",
        "questions": [
            {"q": "¿Qué guardaba el gigante?", "options": ["Oro", "Nubes", "Zapatos", "Agua"], "a": "Nubes"},
            {"q": "¿Cuál era la condición para pedir un deseo?", "options": ["Ir de noche", "Ir sin zapatos", "Llevar un regalo", "Cantar"], "a": "Ir sin zapatos"}
        ]
    },
    {
        "titulo": "El Robot de Cocina",
        "texto": "Arturo compró un robot que cocinaba panqueques. Pero un día, el robot empezó a cocinar calcetines por un error en su cable azul.",
        "questions": [
            {"q": "¿Qué cocinaba originalmente el robot?", "options": ["Pizza", "Panqueques", "Sopa", "Calcetines"], "a": "Panqueques"},
            {"q": "¿Qué causó el error?", "options": ["El cable rojo", "El cable azul", "Mucha harina", "El agua"], "a": "El cable azul"}
        ]
    },
    {
        "titulo": "Abejas Obreras",
        "texto": "Las abejas trabajan todo el día recolectando néctar de las flores. Lo llevan a la colmena para fabricar miel y alimentar a la reina.",
        "questions": [
            {"q": "¿Qué recolectan las abejas?", "options": ["Agua", "Néctar", "Hojas", "Miel"], "a": "Néctar"},
            {"q": "¿Para qué fabrican miel?", "options": ["Para vender", "Para jugar", "Para alimentar a la reina", "Para el invierno"], "a": "Para alimentar a la reina"}
        ]
    },
    {
        "titulo": "El Ciclo del Agua",
        "texto": "El sol calienta el agua de los mares, esta se evapora y forma nubes. Luego cae como lluvia y vuelve al mar, comenzando de nuevo.",
        "questions": [
            {"q": "¿Qué hace el sol con el agua?", "options": ["La enfría", "La calienta", "La desaparece", "La ensucia"], "a": "La calienta"},
            {"q": "¿En qué se convierte el vapor de agua?", "options": ["En nubes", "En hielo", "En sal", "En aire"], "a": "En nubes"}
        ]
    },
    {
        "titulo": "El Perro Astronauta",
        "texto": "Tobi era un perro que soñaba con la luna. Construyó un cohete con cajas de cartón y usó un casco de cristal.",
        "questions": [
            {"q": "¿Con qué soñaba Tobi?", "options": ["Con huesos", "Con la luna", "Con correr", "Con dormir"], "a": "Con la luna"},
            {"q": "¿De qué era su cohete?", "options": ["Metal", "Madera", "Cartón", "Plástico"], "a": "Cartón"}
        ]
    },
    {
        "titulo": "Los Bosques Nativos",
        "texto": "Chile tiene hermosos bosques de araucarias y alerces. Estos árboles viven miles de años y son protegidos por ley.",
        "questions": [
            {"q": "¿Qué árboles se mencionan?", "options": ["Pinos", "Araucarias y alerces", "Palmeras", "Eucaliptus"], "a": "Araucarias y alerces"},
            {"q": "¿Cuánto tiempo viven estos árboles?", "options": ["Pocos años", "Cientos de años", "Miles de años", "Diez años"], "a": "Miles de años"}
        ]
    },
    {
        "titulo": "La Bicicleta de Ana",
        "texto": "Ana recibió una bicicleta roja para su cumpleaños. La usa todos los domingos en el parque con sus primos.",
        "questions": [
            {"q": "¿De qué color es la bicicleta?", "options": ["Azul", "Roja", "Verde", "Amarilla"], "a": "Roja"},
            {"q": "¿Cuándo usa la bicicleta?", "options": ["Los lunes", "Los sábados", "Los domingos", "Todos los días"], "a": "Los domingos"}
        ]
    },
    {
        "titulo": "El Invento de la Imprenta",
        "texto": "Gutenberg inventó la imprenta hace muchos siglos. Esto permitió que más personas pudieran leer libros y aprender cosas nuevas.",
        "questions": [
            {"q": "¿Quién inventó la imprenta?", "options": ["Gutenberg", "Einstein", "Da Vinci", "Newton"], "a": "Gutenberg"},
            {"q": "¿Qué permitió este invento?", "options": ["Viajar rápido", "Leer más libros", "Ver televisión", "Hablar por teléfono"], "a": "Leer más libros"}
        ]
    },
    {
        "titulo": "La Tortuga Gigante",
        "texto": "En las islas Galápagos viven tortugas gigantes que pueden pesar más de 200 kilos. Son animales muy lentos y tranquilos.",
        "questions": [
            {"q": "¿Dónde viven estas tortugas?", "options": ["En la selva", "En las Galápagos", "En el desierto", "En el campo"], "a": "En las Galápagos"},
            {"q": "¿Cuánto pueden pesar?", "options": ["50 kilos", "100 kilos", "Más de 200 kilos", "500 kilos"], "a": "Más de 200 kilos"}
        ]
    }
]

# --- INTERFAZ ---
def main():
    init_db()
    
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    
    if st.session_state.page == 'login':
        login_view()
    elif st.session_state.page == 'assessment':
        assessment_view()
    elif st.session_state.page == 'results':
        results_view()
    elif st.session_state.page == 'admin':
        admin_view()

def login_view():
    st.markdown(f'<h1 style="text-align: center; color: #0056b3;">📝 Ensayo SIMCE Parral</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="neruda-quote">{random.choice(FRASES_MOTIVACIONALES)}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.header("🏠 Acceso Alumnos")
            nombre = st.text_input("Ingresa tu Nombre Completo", placeholder="Ej: Juan Pérez")
            codigo = st.text_input("Código de Curso", placeholder="Ej: 4B")
            if st.button("🚀 Comenzar Evaluación"):
                if nombre and codigo:
                    st.session_state.user = {"nombre": nombre, "codigo": codigo}
                    st.session_state.page = 'assessment'
                    st.rerun()
                else:
                    st.warning("Escribe tu nombre y curso para entrar")
                
    with col2:
        with st.container(border=True):
            st.header("👨‍🏫 Portal Docente")
            pass_code = st.text_input("Clave de Acceso", type="password")
            if st.button("📊 Ver Dashboard"):
                if pass_code == "NERUDA-4B":
                    st.session_state.page = 'admin'
                    st.rerun()
                else:
                    st.error("Clave incorrecta")

def assessment_view():
    st.markdown(f'<h1 style="color: #1e7e34;">🌳 ¡Mucho éxito, {st.session_state.user["nombre"]}!</h1>', unsafe_allow_html=True)
    st.info("Lee cada pregunta con calma. Tienes todo el apoyo de Parral.")
    
    tab1, tab2 = st.tabs(["🔢 Matemática (30 q)", "📚 Comprensión Lectora (10 textos)"])
    
    with tab1:
        respuestas_mat = {}
        for i, p in enumerate(PREGUNTAS_MAT):
            st.markdown(f'<div class="pregunta-card"><b>Pregunta {i+1}:</b><br>{p["q"]}</div>', unsafe_allow_html=True)
            respuestas_mat[i] = st.radio(f"Selecciona tu respuesta ({i+1})", p["options"], key=f"mat_{i}", index=None)
            st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        respuestas_len = {}
        q_idx = 0
        for i, t in enumerate(TEXTOS_LEN):
            st.markdown(f'<div style="text-align: center; color: #d4af37;"><h3>📜 {t["titulo"]}</h3></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="texto-lectura">{t["texto"]}</div>', unsafe_allow_html=True)
            for pq in t["questions"]:
                st.markdown(f'<div class="pregunta-card"><b>Pregunta:</b> {pq["q"]}</div>', unsafe_allow_html=True)
                respuestas_len[q_idx] = st.radio(f"Elige la opción correcta para: {pq['q'][:40]}...", pq["options"], key=f"len_{q_idx}", index=None)
                q_idx += 1
            st.divider()

    if st.button("✅ Terminar Evaluación"):
        # Verificación de completitud simple
        if len([r for r in respuestas_mat.values() if r is not None]) < len(PREGUNTAS_MAT) or \
           len([r for r in respuestas_len.values() if r is not None]) < 20: 
             st.warning("Por favor, responde todas las preguntas antes de finalizar.")
             return
        
        # Calcular Matemática
        correctas_mat = sum(1 for i, p in enumerate(PREGUNTAS_MAT) if respuestas_mat.get(i) == p["a"])
        puntaje_mat = calcular_puntaje_simce(correctas_mat, len(PREGUNTAS_MAT))
        
        # Calcular Lenguaje
        all_len_q = [q for t in TEXTOS_LEN for q in t["questions"]]
        correctas_len = sum(1 for i, p in enumerate(all_len_q) if respuestas_len.get(i) == p["a"])
        puntaje_len = calcular_puntaje_simce(correctas_len, len(all_len_q))
        
        save_result(st.session_state.user['nombre'], st.session_state.user['codigo'], 
                    puntaje_mat, correctas_mat, puntaje_len, correctas_len)
        
        st.session_state.final_results = {
            "p_mat": puntaje_mat, "c_mat": correctas_mat, "total_mat": len(PREGUNTAS_MAT),
            "p_len": puntaje_len, "c_len": correctas_len, "total_len": len(all_len_q)
        }
        st.session_state.page = 'results'
        st.rerun()

def results_view():
    st.balloons()
    res = st.session_state.final_results
    st.markdown('<h1 style="text-align: center; color: #1e7e34;">✨ ¡Lo lograste! ✨</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        medal_text, medal_emoji = obtener_medalla(res['p_mat'])
        st.markdown(f"""
            <div class="medal-container">
                <h2>🔢 Matemática</h2>
                <div style="font-size: 4em;">{medal_emoji}</div>
                <h3>{res['p_mat']} Puntos</h3>
                <p>{medal_text}</p>
                <b>{res['c_mat']} de {res['total_mat']} correctas</b>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        medal_text, medal_emoji = obtener_medalla(res['p_len'])
        st.markdown(f"""
            <div class="medal-container">
                <h2>📚 Lenguaje</h2>
                <div style="font-size: 4em;">{medal_emoji}</div>
                <h3>{res['p_len']} Puntos</h3>
                <p>{medal_text}</p>
                <b>{res['c_len']} de {res['total_len']} correctas</b>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="neruda-quote" style="border-left: 5px solid #1e7e34;">{random.choice(FRASES_MOTIVACIONALES)}</div>', unsafe_allow_html=True)
    
    if st.button("🔙 Volver al Inicio"):
        st.session_state.page = 'login'
        st.rerun()

def admin_view():
    st.title("👨‍🏫 Panel de Control del Profesor")
    st.write("Estadísticas de rendimiento en Parral")
    
    if st.button("← Cerrar Sesión"):
        st.session_state.page = 'login'
        st.rerun()
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM resultados ORDER BY fecha DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No hay resultados registrados aún.")
    else:
        st.header("Rendimiento del Curso")
        c1, c2, c3 = st.columns(3)
        c1.metric("Alumnos", len(df))
        c2.metric("Promedio Mat", f"{int(df['puntaje_mat'].mean())} pts")
        c3.metric("Promedio Len", f"{int(df['puntaje_len'].mean())} pts")
        
        st.header("Distribución de Puntajes")
        fig = px.histogram(df, x=["puntaje_mat", "puntaje_len"], barmode="overlay", 
                          title="Frecuencia de Puntajes", labels={'value':'Puntaje', 'variable':'Materia'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.header("Listado Detallado")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
