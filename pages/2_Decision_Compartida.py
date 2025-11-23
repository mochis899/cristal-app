import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# Importamos la herramienta para mapear números a colores específicos en Matplotlib
from matplotlib.colors import ListedColormap 
from utils import calcular_probabilidad_math, obtener_color_riesgo

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Decisión Compartida CriSTAL", page_icon="🤝", layout="wide")

st.title("🤝 Riesgo CriSTAL: Herramienta de Decisión Compartida")
st.markdown("Traduce la probabilidad numérica en visualizaciones claras para facilitar la comunicación con el paciente y su familia.")

# --- CONTROL DEL SCORE ---
col_input, col_info = st.columns([1, 2])

with col_input:
    # Usamos el mismo valor por defecto que el simulador
    score_paciente = st.number_input(
        "Introduzca el Score CriSTAL Total del paciente:", 
        min_value=0, 
        max_value=20, 
        value=10, 
        step=1
    )

# --- CÁLCULOS PRINCIPALES ---
prob_mortalidad = calcular_probabilidad_math(score_paciente)
prob_supervivencia = 100 - prob_mortalidad
color_final = obtener_color_riesgo(score_paciente)

# Redondeo para el pictograma de 100 personas
n_total = 100
n_muerte = round(prob_mortalidad * (n_total / 100))
n_supervivencia = n_total - n_muerte

# --- VISUALIZACIÓN DE RESULTADOS ---
with col_info:
    st.subheader("Resultado Estimado a 30 Días")
    st.markdown(
        f"""
        <div style="background-color:{color_final}15; border: 2px solid {color_final}; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="color: {color_final}; margin:0; font-size: 1.1em; font-weight:bold;">SCORE TOTAL OBTENIDO</p>
            <h1 style="color: {color_final}; margin: 5px 0 10px 0; font-size: 3em;">{score_paciente} / 20</h1>
            <p style="color: black; font-size: 1.2em; margin:0;">Probabilidad Estimada de Mortalidad: <b>{prob_mortalidad:.1f}%</b></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- GRÁFICOS ---
st.markdown("---")
st.subheader("Representación del Riesgo")

col_pie, col_waffle = st.columns(2)

# --- 1. GRÁFICO DE PASTEL (PIE CHART) ---
with col_pie:
    st.markdown("#### 1. Diagrama de Pastel (Proporción)")
    
    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    
    # Datos para el pastel
    sizes = [prob_supervivencia, prob_mortalidad]
    labels = [f'Supervivencia ({prob_supervivencia:.1f}%)', f'Mortalidad ({prob_mortalidad:.1f}%)']
    colors = ['#2ecc71', color_final] # Verde y el color del riesgo
    explode = (0, 0.1) # Resaltar la mortalidad
    
    # Dibujar el pastel
    ax_pie.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=colors, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    ax_pie.axis('equal') # Asegura que el pastel sea un círculo
    ax_pie.set_title("Pronóstico a 30 Días", fontsize=16)
    
    st.pyplot(fig_pie)
    
    st.info(f"El **{prob_mortalidad:.1f}%** de probabilidad se concentra en el riesgo de mortalidad.")


# --- 2. PICTOGRAMA (WAFFLE CHART de 100 Personas) ---
with col_waffle:
    st.markdown("#### 2. Pictograma (100 Personas)")
    
    # 1. Crear el array de CATEGORÍAS (0 para supervivencia, 1 para riesgo)
    categoria_riesgo = 1
    categoria_supervivencia = 0
    
    # Llenar la lista con las categorías numéricas
    categorias_waffle = [categoria_riesgo] * n_muerte + [categoria_supervivencia] * n_supervivencia
    
    # Asegurarse de que la lista tiene 100 elementos
    categorias_waffle = categorias_waffle[:100]
    
    # Barajar para que no sean bloques perfectos
    np.random.shuffle(categorias_waffle)

    # Convertir a matriz 10x10 para la visualización
    matriz_numerica = np.array(categorias_waffle).reshape((10, 10))
    
    # 2. DEFINIR EL MAPA DE COLORES (El arreglo que faltaba)
    cmap_colors = [
        '#2ecc71',   # Categoría 0: Supervivencia (Verde)
        color_final  # Categoría 1: Mortalidad (Color de riesgo específico)
    ]
    # Crear el colormap usando la lista de colores
    cmap = ListedColormap(cmap_colors)
    
    fig_waffle, ax_waffle = plt.subplots(figsize=(7, 7))
    
    # 3. Mostrar la imagen usando la matriz numérica y el colormap
    ax_waffle.imshow(matriz_numerica, cmap=cmap, aspect='auto') 
    
    # Dibujar las celdas (cuadrados)
    for i in range(10):
        for j in range(10):
            rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor='grey', linewidth=0.5, alpha=0.5)
            ax_waffle.add_patch(rect)
            
    ax_waffle.set_title(f"De cada 100 personas como esta...", fontsize=16)
    ax_waffle.axis('off') # Quitar ejes
    
    st.pyplot(fig_waffle)
    
    st.warning(f"De cada **100 personas** con este perfil de riesgo, estadísticamente **{n_muerte}** no sobrevivirían al mes de la cirugía.")
    
st.markdown("---")

# --- MENSAJE PARA EL PACIENTE ---
st.subheader("Comunicación Clínica Recomendada")

if score_paciente < 8:
    st.success("El riesgo es bajo. La probabilidad de que la cirugía sea exitosa es muy alta. Proceder con el plan quirúrgico es la mejor opción.")
elif score_paciente < 12:
    st.warning("El riesgo es moderado. La mayoría de las personas superan la cirugía, pero hay un riesgo real. Es crucial optimizar su estado físico antes de operar, si es posible.")
elif score_paciente < 14:
    st.error("El riesgo es alto. La posibilidad de un desenlace fatal es significativa. Debemos considerar muy seriamente si los beneficios de la cirugía superan los riesgos, o buscar alternativas no quirúrgicas.")
else:
    st.error("El riesgo es crítico. El riesgo de mortalidad supera el 50%. La cirugía solo se debe plantear en casos de extrema urgencia y con el consentimiento informado de un riesgo altísimo.")
