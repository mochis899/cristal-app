import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils import calcular_probabilidad_math, obtener_color_riesgo

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador CriSTAL Interactivo", page_icon="📈", layout="wide")

st.title("📈 Simulador de Riesgo CriSTAL")
st.markdown("Mueve el deslizador para ver cómo el Score Total afecta la probabilidad de mortalidad.")

# Configuración estética de la gráfica
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# --- CONTROL DEL SIMULADOR ---
score_simulado = st.slider(
    "Selecciona un Score Total (0 a 20)", 
    min_value=0, 
    max_value=20, 
    value=10, 
    step=1
)

# --- CÁLCULOS ---
prob_simulada = calcular_probabilidad_math(score_simulado)
color_simulado = obtener_color_riesgo(score_simulado)

# --- VISUALIZACIÓN ---
col_metric, col_dummy = st.columns([1, 2])

with col_metric:
    st.metric("Score Actual", f"{score_simulado} / 20")
    st.markdown(
        f"""
        <div style="background-color:{color_simulado}20; border: 2px solid {color_simulado}; border-radius: 5px; padding: 10px; text-align: center;">
            <p style="color: {color_simulado}; margin:0; font-weight:bold;">Mortalidad Estimada</p>
            <h2 style="color: {color_simulado}; margin:0;">{prob_simulada:.1f}%</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
st.write("") # Espaciador

# --- GENERACIÓN DE LA GRÁFICA ---
fig, ax = plt.subplots(figsize=(10, 5))

# 1. Rango X y Y (Usando NumPy para evitar errores)
x = np.arange(0, 20.1, 0.1)
y = calcular_probabilidad_math(x) # Vectorización directa

# 2. Dibujar zonas (Fondo)
ax.axvspan(0, 8, color='#2ecc71', alpha=0.1)
ax.axvspan(8, 12, color='#f1c40f', alpha=0.1)
ax.axvspan(12, 14, color='#e67e22', alpha=0.1)
ax.axvspan(14, 20, color='#e74c3c', alpha=0.1)

# 3. Dibujar curva
ax.plot(x, y, color='black', alpha=0.6, linewidth=2)

# 4. PUNTO DE LA SIMULACIÓN
ax.scatter(score_simulado, prob_simulada, s=300, color=color_simulado, edgecolors='black', zorder=10)

# 5. Líneas guía
ax.axvline(score_simulado, color=color_simulado, linestyle='--', ymax=prob_simulada/100)
ax.axhline(prob_simulada, color=color_simulado, linestyle='--', xmax=score_simulado/20)

# Ajustes finales
ax.set_xlim(0, 20)
ax.set_ylim(0, 100)
ax.set_xlabel("Score Total (Puntos)", fontweight='bold')
ax.set_ylabel("Probabilidad (%)", fontweight='bold')
ax.set_title("Curva de Riesgo CriSTAL", fontsize=16)
ax.grid(True, linestyle=':', alpha=0.5)

st.pyplot(fig)

# Mensaje clínico final
if score_simulado < 8:
    st.info("🟢 **Riesgo Bajo:** Buen candidato para cirugía estándar.")
elif score_simulado < 12:
    st.warning("🟡 **Riesgo Intermedio:** Requiere optimización preoperatoria.")
elif score_simulado < 14:
    st.warning("🟠 **Riesgo Alto:** Mortalidad significativamente elevada. Valorar alternativa.")
else:
    st.error("🔴 **Riesgo Crítico:** Mortalidad superior al 50%. Pronóstico muy reservado.")
