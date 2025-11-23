import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador CriSTAL Interactivo", page_icon="🎚️", layout="wide")

# --- FUNCIONES MATEMÁTICAS ---
def calcular_probabilidad(score):
    # Fórmula Logística Tesis
    logit = -3.844 + (0.285 * score)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color_riesgo(score):
    if score < 8: return "#2ecc71"   # Verde (Bajo)
    elif score < 12: return "#f1c40f" # Amarillo (Intermedio)
    elif score < 14: return "#e67e22" # Naranja (Alto)
    else: return "#e74c3c"            # Rojo (Crítico)

# --- INTERFAZ DE USUARIO ---
st.title("🎚️ Simulador de Riesgo CriSTAL: Efecto de las Variables")
st.markdown("Selecciona las variables clínicas a la izquierda y observa cómo impactan en el riesgo de mortalidad en tiempo real.")

# Dividir la pantalla en 2 columnas: Controles (Izquierda) y Visualización (Derecha)
col_controles, col_visual = st.columns([1, 2])

# --- COLUMNA IZQUIERDA: CONTROLES (VARIABLES) ---
with col_controles:
    st.subheader("Variables Clínicas")
    
    # Inicializar puntos
    pts = 0
    
    # 1. EDAD
    if st.checkbox("1. Edad > 65 años (+1)"): pts += 1
    
    # 2. RESIDENCIA
    if st.checkbox("2. Vive en Residencia/Asilo (+1)"): pts += 1
    
    # 3. FISIOLÓGICO (Simulado como un solo check para simplificar el simulador)
    if st.checkbox("3. Estado Fisiológico (≥2 alt.) (+1)"): pts += 1
    
    # 4. COMORBILIDADES (Multi-select para sumar hasta 7 puntos)
    st.markdown("**4. Comorbilidades (+1 c/u):**")
    comorbs = st.multiselect("Selecciona patologías:", 
        ["Cáncer", "IRC", "ICC", "EPOC", "ACV", "IAM", "Hepatopatía"])
    pts += len(comorbs)
    
    # 5-8. OTROS
    st.markdown("**Otros Factores (+1 c/u):**")
    if st.checkbox("5. Deterioro Cognitivo"): pts += 1
    if st.checkbox("6. Ingreso Previo (<1 año)"): pts += 1
    if st.checkbox("7. Proteinuria"): pts += 1
    if st.checkbox("8. ECG Anormal"): pts += 1
    
    # 9. FRAGILIDAD (Multi-select para sumar hasta 5 puntos)
    st.markdown("**9. Fragilidad FRAIL (+1 c/u):**")
    frail = st.multiselect("Selecciona ítems FRAIL:", 
        ["Fatiga", "Resistencia", "Deambulación", "Enfermedades", "Pérdida Peso"])
    pts += len(frail)

    # Limitar a 20 por si acaso (aunque la suma lógica lo limita)
    score_final = min(pts, 20)

# --- CÁLCULOS ---
prob_actual = calcular_probabilidad(score_final)
color_actual = obtener_color_riesgo(score_final)

# --- COLUMNA DERECHA: VISUALIZACIÓN ---
with col_visual:
    # 1. TARJETAS DE RESULTADO
    c1, c2 = st.columns(2)
    c1.metric("Score Total", f"{score_final} / 20")
    
    # HTML para mostrar la probabilidad en grande y con color
    c2.markdown(
        f"""
        <div style="background-color:{color_actual}20; border: 2px solid {color_actual}; border-radius: 5px; padding: 0px 10px; text-align: center;">
            <p style="color: {color_actual}; margin:0; font-weight:bold;">Probabilidad Mortalidad</p>
            <h2 style="color: {color_actual}; margin:0;">{prob_actual:.1f}%</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 2. GRÁFICA DINÁMICA
    st.write("") # Espacio
    
    # Generar datos para la curva
    x_range = np.arange(0, 20.1, 0.1)
    y_range = [calcular_probabilidad(x) for x in x_range]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Zonas de riesgo (Fondo)
    ax.axvspan(0, 8, color='#2ecc71', alpha=0.1)
    ax.axvspan(8, 12, color='#f1c40f', alpha=0.1)
    ax.axvspan(12, 14, color='#e67e22', alpha=0.1)
    ax.axvspan(14, 20, color='#e74c3c', alpha=0.1)

    # Curva
    ax.plot(x_range, y_range, color='black', linewidth=2, alpha=0.5)

    # PUNTO DINÁMICO
    ax.scatter(score_final, prob_actual, color=color_actual, s=250, zorder=10, edgecolors='black', label='Tu Paciente')

    # Líneas guía
    ax.axvline(score_final, color=color_actual, linestyle='--', ymax=prob_actual/100)
    ax.axhline(prob_actual, color=color_actual, linestyle='--', xmax=score_final/20)

    # Etiquetas
    ax.set_xlabel("Score Total", fontweight='bold')
    ax.set_ylabel("Probabilidad (%)", fontweight='bold')
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(0, 21, 2))
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Texto explicativo de las zonas
    ax.text(4, 5, "Bajo", color='#27ae60', ha='center', fontweight='bold')
    ax.text(10, 5, "Intermedio", color='#f39c12', ha='center', fontweight='bold')
    ax.text(13, 5, "Alto", color='#d35400', ha='center', fontweight='bold')
    ax.text(17, 5, "Crítico", color='#c0392b', ha='center', fontweight='bold')

    st.pyplot(fig)

    # 3. MENSAJE CLÍNICO
    if score_final < 8:
        msg = "🟢 **Zona Segura:** El riesgo es bajo. El paciente es buen candidato para cirugía estándar."
    elif score_final < 12:
        msg = "🟡 **Zona de Alerta:** El riesgo se eleva. Requiere optimización preoperatoria."
    elif score_final < 14:
        msg = "🟠 **Zona de Peligro:** La mortalidad es alta (>38%). Evaluar riesgo/beneficio cuidadosamente."
    else:
        msg = "🔴 **Zona Crítica:** La mortalidad supera el 50%. La cirugía tiene un pronóstico muy reservado."
    
    st.info(msg)
