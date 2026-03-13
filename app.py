import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SIMCE Simulator Premium", page_icon="📊", layout="wide")

# Estilos CSS personalizados para un look premium
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pregunta-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .texto-lectura {
        background-color: #fff3cd;
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        font-family: 'Georgia', serif;
        font-size: 1.1em;
        line-height: 1.6;
        border: 1px solid #ffeeba;
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
    # Tabla de resultados
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
    # Escala lineal simple de 200 a 400
    return int(200 + (porcentaje * 200))

# --- CONTENIDO: MATEMÁTICA (30 preguntas) ---
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

# --- CONTENIDO: LENGUAJE (10 textos) ---
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
    st.title("🚀 Simulador SIMCE Premium")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Acceso Alumnos")
        nombre = st.text_input("Nombre Completo")
        codigo = st.text_input("Código de Curso (Ej: 4B)")
        if st.button("Comenzar Evaluación"):
            if nombre and codigo:
                st.session_state.user = {"nombre": nombre, "codigo": codigo}
                st.session_state.page = 'assessment'
                st.rerun()
            else:
                st.error("Por favor completa los datos")
                
    with col2:
        st.header("Portal Docente")
        pass_code = st.text_input("Código de Profesor", type="password")
        if st.button("Ingresar Dashboard"):
            if pass_code == "NERUDA-4B":
                st.session_state.page = 'admin'
                st.rerun()
            else:
                st.error("Código incorrecto")

def assessment_view():
    st.title(f"📖 Evaluación en curso: {st.session_state.user['nombre']}")
    
    tab1, tab2 = st.tabs(["🔢 Matemática", "📚 Comprensión Lectora"])
    
    with tab1:
        respuestas_mat = {}
        for i, p in enumerate(PREGUNTAS_MAT):
            st.markdown(f'<div class="pregunta-card"><b>Pregunta {i+1}:</b> {p["q"]}</div>', unsafe_allow_html=True)
            respuestas_mat[i] = st.radio(f"Selecciona tu respuesta ({i+1})", p["options"], key=f"mat_{i}")
            st.divider()

    with tab2:
        respuestas_len = {}
        q_idx = 0
        for i, t in enumerate(TEXTOS_LEN):
            st.markdown(f"### {t['titulo']}")
            st.markdown(f'<div class="texto-lectura">{t["texto"]}</div>', unsafe_allow_html=True)
            for pq in t["questions"]:
                st.markdown(f'<b>Pregunta:</b> {pq["q"]}')
                respuestas_len[q_idx] = st.radio(f"Respuesta para: {pq['q'][:30]}...", pq["options"], key=f"len_{q_idx}")
                q_idx += 1
            st.divider()

    if st.button("Finalizar y Ver Resultados"):
        # Calcular Matemática
        correctas_mat = sum(1 for i, p in enumerate(PREGUNTAS_MAT) if respuestas_mat[i] == p["a"])
        puntaje_mat = calcular_puntaje_simce(correctas_mat, len(PREGUNTAS_MAT))
        
        # Calcular Lenguaje
        # Mapeo plano de todas las preguntas de lenguaje para facilitar conteo
        all_len_q = [q for t in TEXTOS_LEN for q in t["questions"]]
        correctas_len = sum(1 for i, p in enumerate(all_len_q) if respuestas_len[i] == p["a"])
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
    st.title("🏆 Tus Resultados")
    res = st.session_state.final_results
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Puntaje Matemática", f"{res['p_mat']} pts", f"{res['c_mat']}/{res['total_mat']} correctas")
    with col2:
        st.metric("Puntaje Comprensión Lectora", f"{res['p_len']} pts", f"{res['c_len']}/{res['total_len']} correctas")
        
    st.success("¡Felicidades por completar el ensayo! Tus resultados han sido guardados.")
    if st.button("Volver al Inicio"):
        st.session_state.page = 'login'
        st.rerun()

def admin_view():
    st.title("👨‍🏫 Dashboard del Profesor - Código: NERUDA-4B")
    
    if st.button("← Salir"):
        st.session_state.page = 'login'
        st.rerun()
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM resultados ORDER BY fecha DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("Aún no hay resultados registrados.")
    else:
        st.header("Resumen del Curso")
        c1, c2, c3 = st.columns(3)
        c1.metric("Estudiantes Evaluados", len(df))
        c2.metric("Promedio Matemática", f"{int(df['puntaje_mat'].mean())} pts")
        c3.metric("Promedio Lenguaje", f"{int(df['puntaje_len'].mean())} pts")
        
        st.header("Gráfico de Rendimiento")
        fig = px.scatter(df, x="puntaje_mat", y="puntaje_len", hover_data=["nombre"], 
                        size_max=60, title="Matemática vs Lenguaje")
        st.plotly_chart(fig, use_container_width=True)
        
        st.header("Detalle por Estudiante")
        st.dataframe(df.style.highlight_max(axis=0, subset=["puntaje_mat", "puntaje_len"]))

if __name__ == "__main__":
    main()
