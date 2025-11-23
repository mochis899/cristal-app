import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Simulador CriSTAL V2", page_icon="🎚️", layout="wide")

# Configuración estética de las gráficas
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# --- 2. FUNCIONES MATEMÁTICAS ---
def calcular_probabilidad(score):
    # L = -3.844 + 0.285 * Score
    logit = -3.844 + (0.285 * score)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color(score):
    if score < 8: return "#2ecc71"   # Verde
    elif score < 12: return "#f1c40f" # Amarillo
    elif score < 14: return "#e67e22" # Naranja
    else: return "#e74c3c"            # Rojo

# --- 3. INTERFAZ ---
st.title("🎚️ Simulador Interactivo CriSTAL")
st.info("ℹ️ Haz clic en los recuadros. El cálculo debe actualizarse AUTOMÁTICAMENTE.")

col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.subheader("📝 Marca las casillas:")
    
    # --- SUMA EN TIEMPO REAL ---
    puntos = 0
    
    # Checkboxes directos (sin formularios)
    if st.checkbox("1. Edad > 65 años (+1)", value=True): puntos += 1
    if st.checkbox("2. Residencia / Asilo (+1)"): puntos += 1
    if st.checkbox("3. Estado Fisiológico Agudo (+1)", value=True): puntos += 1
    
    st.markdown("---")
    # Comorbilidades
    comorbilidades = st.multiselect("4. Comorbilidades (+1 c/u):", 
        ["Cáncer", "Insuf. Renal", "Insuf. Cardíaca", "EPOC", "ACV", "IAM", "Hepatopatía"],
        default=["Cáncer", "Insuf. Renal", "Insuf. Cardíaca", "EPOC", "ACV"]) # Default para que coincida con tu ejemplo
    puntos += len(comorbilidades)
    
    st.markdown("---")
    # Otros factores
    if st.checkbox("5. Deterioro Cognitivo (+1)"): puntos += 1
    if st.checkbox("6. Ingreso Previo (+1)"): puntos += 1
    if st.checkbox("7. Proteinuria (+1)"): puntos += 1
    if st.checkbox("8. ECG Anormal (+1)"): puntos += 1
    
    st.markdown("---")
    # Fragilidad
    fragilidad = st.multiselect("9. Fragilidad FRAIL (+1 c/u):", 
        ["Fatiga", "Resistencia", "Deambulación", "Enfermedades", "Pérdida Peso"])
    puntos += len(fragilidad)

    # Límite máximo
    score_final = min(puntos, 20)
    
    # DEBUG VISUAL: Verificamos que el contador funcione
    st.write(f"🔢 **Puntos contados:** {puntos}")


# --- 4. CÁLCULOS Y GRÁFICA ---
prob_actual = calcular_probabilidad(score_final)
color_actual = obtener_color(score_final)

with col_der:
    # Tarjetas Superiores
    c1, c2 = st.columns(2)
    c1.metric("Score Total", f"{score_final} / 20")
    
    # Tarjeta de Probabilidad con color dinámico
    c2.markdown(f"""
    <div style="background-color:{color_actual}20; border:2px solid {color_actual}; border-radius:5px; padding:10px; text-align:center;">
        <strong style="color:{color_actual}">Probabilidad Mortalidad</strong>
        <h1 style="color:{color_actual}; margin:0;">{prob_actual:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)

    st.write("") # Espaciador

    # --- GENERACIÓN DE LA GRÁFICA ---
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 1. Rango X y Y (Usando NumPy para evitar errores de lista)
    x = np.arange(0, 20.1, 0.1)
    y = calcular_probabilidad(x) # Vectorización directa

    # 2. Dibujar zonas
    ax.axvspan(0, 8, color='#2ecc71', alpha=0.1)
    ax.axvspan(8, 12, color='#f1c40f', alpha=0.1)
    ax.axvspan(12, 14, color='#e67e22', alpha=0.1)
    ax.axvspan(14, 20, color='#e74c3c', alpha=0.1)

    # 3. Dibujar curva
    ax.plot(x, y, color='black', alpha=0.6, linewidth=2)

    # 4. PUNTO DEL PACIENTE (Grande y visible)
    ax.scatter(score_final, prob_actual, s=300, color=color_actual, edgecolors='black', zorder=10)
    
    # 5. Líneas guía
    ax.axvline(score_final, color=color_actual, linestyle='--', ymax=prob_actual/100)
    ax.axhline(prob_actual, color=color_actual, linestyle='--', xmax=score_final/20)

    # Ajustes finales
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Score Total (Puntos)", fontweight='bold')
    ax.set_ylabel("Probabilidad (%)", fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)

    st.pyplot(fig)
    
