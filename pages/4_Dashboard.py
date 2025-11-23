import streamlit as st
import pandas as pd
import altair as alt
from utils import get_mock_patient_data, obtener_color_riesgo, categorizar_score

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard CriSTAL", page_icon="📊", layout="wide")

# Cargar datos simulados
df = get_mock_patient_data()

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("📊 Dashboard de Cohorte de Pacientes")
st.markdown("Visualización analítica de los pacientes registrados en el sistema CriSTAL.")
st.caption(f"Mostrando datos simulados de {len(df)} pacientes.")

# --- 1. MÉTRICAS CLAVE (KPIs) ---
st.subheader("Métricas de Cohorte")
col1, col2, col3, col4 = st.columns(4)

total_pacientes = len(df)
avg_score = df['Score_CriSTAL'].mean()
pacientes_alto_critico = df[df['Categoria_Riesgo'].str.startswith('3') | df['Categoria_Riesgo'].str.startswith('4')]

col1.metric("Pacientes Registrados", total_pacientes)
col2.metric("Score CriSTAL Promedio", f"{avg_score:.1f}")
col3.metric("Mortalidad Media Estimada", f"{df['Prob_Mortalidad'].mean():.1f}%")
col4.metric("Riesgo Alto/Crítico", f"{len(pacientes_alto_critico)}", 
            delta=f"{(len(pacientes_alto_critico) / total_pacientes * 100):.1f}% del total")

st.markdown("---")

# --- 2. DISTRIBUCIÓN DEL RIESGO ---
st.subheader("Distribución de Riesgo CriSTAL")

# Preparar datos para el gráfico de barras/tarta
df_dist = df.groupby('Categoria_Riesgo').size().reset_index(name='Cuenta')
df_dist['Porcentaje'] = (df_dist['Cuenta'] / total_pacientes) * 100

# Obtener colores fijos para las categorías (para consistencia)
color_map = {
    '1. Bajo (<8)': obtener_color_riesgo(0),      # Verde
    '2. Intermedio (8-11)': obtener_color_riesgo(10), # Amarillo
    '3. Alto (12-13)': obtener_color_riesgo(13),   # Naranja
    '4. Crítico (>13)': obtener_color_riesgo(15)   # Rojo
}

# Gráfico de barras
chart_bar = alt.Chart(df_dist).mark_bar().encode(
    x=alt.X('Categoria_Riesgo', title='Categoría de Riesgo'),
    y=alt.Y('Cuenta', title='Nº de Pacientes'),
    tooltip=['Categoria_Riesgo', 'Cuenta', alt.Tooltip('Porcentaje', format='.1f')],
    color=alt.Color('Categoria_Riesgo', 
                    scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())),
                    legend=None
                   )
).properties(
    title='Pacientes por Nivel de Riesgo'
).interactive() # Habilitar zoom y paneo

st.altair_chart(chart_bar, use_container_width=True)

st.markdown("---")

# --- 3. ANÁLISIS DE FACTORES DE RIESGO ---
st.subheader("Frecuencia de Factores Específicos")

# Preparar datos para el gráfico de factores
factor_cols = ['Edad_65+', 'Fragilidad', 'Comorbilidad_ICC', 'Comorbilidad_EPOC', 
               'Fisiologico_Agudo', 'Deterioro_Cognitivo']

# Contar la frecuencia de los factores activos (True)
factor_counts = df[factor_cols].sum().reset_index()
factor_counts.columns = ['Factor', 'Cuenta']

# Renombrar factores para una mejor visualización en el gráfico
factor_counts['Factor'] = factor_counts['Factor'].replace({
    'Edad_65+': 'Edad > 65',
    'Fragilidad': 'Síndrome de Fragilidad',
    'Comorbilidad_ICC': 'Insuficiencia Cardíaca (ICC)',
    'Comorbilidad_EPOC': 'EPOC',
    'Fisiologico_Agudo': 'Alteración Fisiológica Aguda',
    'Deterioro_Cognitivo': 'Deterioro Cognitivo',
})

# Gráfico de barras horizontales
chart_factors = alt.Chart(factor_counts).mark_bar().encode(
    x=alt.X('Cuenta', title='Recuento de Pacientes con Factor Activo'),
    y=alt.Y('Factor', sort='x', title='Factor de Riesgo'),
    color=alt.value('#3498db'), # Color azul para destacar los factores
    tooltip=['Factor', 'Cuenta']
).properties(
    title='Factores de Riesgo más Prevalentes'
).interactive()

st.altair_chart(chart_factors, use_container_width=True)

st.markdown("---")
st.info("💡 **Conclusión del Dashboard:** El dashboard permite identificar rápidamente si la mayoría de los pacientes se encuentran en riesgo bajo o si existe una alta carga de riesgo, y en qué factores específicos debemos concentrar los esfuerzos de prehabilitación.")
