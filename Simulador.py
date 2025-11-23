import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador CriSTAL Interactivo", page_icon="🎚️", layout="wide")

# --- FUNCIONES MATEMÁTICAS ---
def calcular_probabilidad(score):
    # Al usar np.exp, esta función acepta tanto números sueltos como arrays enteros
    logit = -3.844 + (0.285 * score)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color_riesgo(score):
    if score < 8: return "#2ecc71"   # Verde (Bajo)
    elif score < 12: return "#f1c40f" # Amarillo (Intermedio)
    elif score < 14: return "#e67e22" # Naranja (Alto)
    else: return "#e74c3c"            # Rojo (Crítico)

# --- INTERFAZ DE USUARIO ---
st.title("🎚️ Simulador de Riesgo CriSTAL")
st.markdown("Selecciona las variables clínicas para ver el impacto en el riesgo en tiempo real.")

# Dividir la pantalla en 2 columnas
col_controles, col_visual = st.columns([1, 2])

# --- COLUMNA IZQUIERDA: CONTROLES ---
with col_controles:
    st.subheader("Variables del Paciente")
    
    pts = 0
    
    # Variables individuales
    if st.checkbox("1. Edad > 65 años (+1)"): pts += 1
    if st.checkbox("2. Vive en Residencia/Asilo (+1)"): pts += 1
    if st.checkbox("3. Estado Fisiológico (≥2 alt.) (+1)"): pts += 1
    
    st.markdown("**4. Comorbilidades (+1 c/u):**")
    comorbs = st.multiselect("Selecciona patologías:", 
        ["Cáncer", "IRC", "ICC", "EPOC", "ACV", "IAM", "Hepatopatía"])
    pts += len(comorbs)
    
    st.markdown("**Otros Factores (+1 c/u):**")
    if st.checkbox("5. Deterioro Cognitivo"): pts += 1
    if st.checkbox("6. Ingreso Previo (<1 año)"): pts += 1
    if st.checkbox("7. Proteinuria"): pts += 1
    if st.checkbox("8. ECG Anormal"): pts += 1
    
    st.markdown("**9. Fragilidad FRAIL (+1 c/u):**")
    frail = st.multiselect("Selecciona ítems FRAIL:", 
        ["Fatiga", "Resistencia", "Deambulación", "Enfermedades", "Pérdida Peso"])
    pts += len(frail)

    # Score final (máximo 20)
    score_final = min(pts, 20)

# --- CÁLCULOS ---
prob_actual = calcular_probabilidad(score_final)
color_actual = obtener_color_riesgo(score_final)

# --- COLUMNA DERECHA: VISUALIZACIÓN ---
with col_visual:
    # Tarjetas de resultado
    c1, c2 = st.columns(2)
    c1.metric("Score Total", f"{score_final} / 20")
    
    c2.markdown(
        f"""
        <div style="background-color:{color_actual}20; border: 2px solid {color_actual}; border-radius: 5px; padding: 0px 10px; text-align: center;">
            <p style="color: {color_actual}; margin:0; font-weight:bold;">Probabilidad Mortalidad</p>
            <h2 style="color: {color_actual}; margin:0;">{prob_actual:.1f}%</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.write("") # Espacio
    
    # --- GENERACIÓN DE LA GRÁFICA ---
    
    # 1. Definir rango X (Score 0 a 20)
    # Creamos un array de numpy
    x_range = np.arange(0, 20.1, 0.1)
    
    # 2. Definir rango Y (Probabilidades)
    # 🚨 CORRECCIÓN DEFINITIVA: 
    # Pasamos el array 'x_range' directamente a la función. 
    # Esto devuelve automáticamente un array de numpy, evitando las listas de Python.
    y_range = calcular_probabilidad(x_range)

    fig, ax = plt.subplots(figsize=(10, 5))

    # Dibujar zonas de riesgo (Fondo de color)
    ax.axvspan(0, 8, color='#2ecc71', alpha=0.1)   # Bajo
    ax.axvspan(8, 12, color='#f1c40f', alpha=0.1)  # Intermedio
    ax.axvspan(12, 14, color='#e67e22', alpha=0.1) # Alto
    ax.axvspan(14, 20, color='#e74c3c', alpha=0.1) # Crítico

    # Dibujar la curva negra principal
    ax.plot(x_range, y_range, color='black', linewidth=2, alpha=0.6)
    
    # Opcional: Rellenar área roja si supera el 50%
    # Ahora 'y_range' es 100% seguro un array numérico, por lo que la comparación >= 50 funcionará.
    ax.fill_between(x_range, y_range, 50, where=(y_range >= 50), color='red', alpha=0.2)

    # Dibujar el PUNTO DEL PACIENTE
    ax.scatter(score_final, prob_actual, color=color_actual, s=250, zorder=10, edgecolors='black', label='Tu Paciente')

    # Líneas guía hacia los ejes
    ax.axvline(score_final, color=color_actual, linestyle='--', ymax=prob_actual/100)
    ax.axhline(prob_actual, color=color_actual, linestyle='--', xmax=score_final/20)

    # Etiquetas y estilo
    ax.set_xlabel("Score Total", fontweight='bold')
    ax.set_ylabel("Probabilidad (%)", fontweight='bold')
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(0, 21, 2))
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Texto de las zonas
    ax.text(4, 5, "Bajo", color='#27ae60', ha='center', fontweight='bold')
    ax.text(10, 5, "Intermedio", color='#f39c12', ha='center', fontweight='bold')
    ax.text(13, 5, "Alto", color='#d35400', ha='center', fontweight='bold')
    ax.text(17, 5, "Crítico", color='#c0392b', ha='center', fontweight='bold')

    st.pyplot(fig)

    # Mensaje clínico final
    if score_final < 8:
        st.info("🟢 **Zona Segura:** El riesgo es bajo. Buen candidato para cirugía estándar.")
    elif score_final < 12:
        st.warning("🟡 **Zona de Alerta:** El riesgo se eleva. Requiere optimización.")
    elif score_final < 14:
        st.warning("🟠 **Zona de Peligro:** La mortalidad es alta (>38%). Valorar riesgo/beneficio.")
    else:
        st.error("🔴 **Zona Crítica:** La mortalidad supera el 50%. Pronóstico muy reservado.")
    
