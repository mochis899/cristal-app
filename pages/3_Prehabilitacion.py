import streamlit as st
import pandas as pd
from utils import obtener_color_riesgo
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Plan de Prehabilitación", page_icon="💪", layout="wide")

st.title("💪 Plan de Prehabilitación y Optimización Específico")
st.markdown("Recomendaciones basadas en los factores de riesgo marcados en la Calculadora CriSTAL.")

# --- CONEXIÓN DE SESIÓN Y CÁLCULOS ---
score_final = st.session_state.get('current_score')
factores = st.session_state.get('current_factors', {})

# Fallback si no hay score en la sesión
if score_final is None:
    st.error("⚠️ **ERROR:** No se ha calculado el Score CriSTAL. Por favor, ve a la página 'Calculadora CriSTAL' primero.")
    score_final = 0 # Usar 0 para evitar errores de cálculo
    
color_final = obtener_color_riesgo(score_final)

# Extraer factores relevantes para el plan
p_edad = factores.get('p_edad', 0) > 0
p_residencia = factores.get('p_residencia', False)
p_fisiologico = factores.get('p_fisiologico', 0) > 0
p_cognitivo = factores.get('p_cognitivo', False)
p_comorb = factores.get('p_comorb', 0) > 0
comorb_detalles = factores.get('comorb_detalles', [])
p_fragilidad = factores.get('p_fragilidad', 0) > 0
frag_detalles = factores.get('frag_detalles', [])

# --- RESUMEN Y PLAN ---

col_resumen, col_plan = st.columns([1, 2])

# Columna de Resumen
with col_resumen:
    st.markdown("#### Score Resumen")
    st.markdown(
        f"""
        <div style="background-color:{color_final}15; border: 2px solid {color_final}; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px;">
            <p style="color: {color_final}; margin:0; font-size: 1.1em; font-weight:bold;">SCORE TOTAL OBTENIDO</p>
            <h1 style="color: {color_final}; margin: 5px 0 10px 0; font-size: 3em;">{score_final}</h1>
        </div>
        <p style='text-align:center;'>*Datos obtenidos de la Calculadora CriSTAL*</p>
        """, 
        unsafe_allow_html=True
    )
    
    if score_final < 8:
        st.success("Riesgo Bajo. Las medidas de optimización estándar son suficientes.")
    elif score_final < 12:
        st.warning("Riesgo Intermedio. La prehabilitación intensiva puede mejorar significativamente el pronóstico.")
    else:
        st.error("Riesgo Alto/Crítico. La prehabilitación es crucial. Se debe valorar la no-cirugía si no hay mejoría tras la optimización.")

# Columna del Plan
with col_plan:
    st.markdown("#### 2. Plan de Optimización Específico")
    
    plan_generado = False
    
    # 1. Optimización Fisiológica Aguda (V3)
    if p_fisiologico:
        st.header("1️⃣ Estabilización Fisiológica (V3)")
        st.error("🚨 **¡NO OPERAR!** Tratar estas alteraciones antes de cualquier cirugía electiva.")
        st.write("""
        * **Objetivo:** Estabilizar TA, FR, Pulso y Saturación. Corregir hipoglucemia y trastornos de conciencia.
        * **Acción:** Monitorización intensiva, reanimación de fluidos si necesario, ajuste de medicación y/o ingreso en UCI.
        """)
        plan_generado = True

    # 2. Optimización de Comorbilidades (V4)
    if p_comorb:
        st.header("2️⃣ Manejo de Comorbilidades (V4)")
        st.warning("Se requiere interconsulta especializada y/o intensificación del tratamiento de base.")
        
        if any(c in comorb_detalles for c in ["ICC", "IAM Reciente", "ACV Reciente"]):
             st.info("🩺 **Cardiovascular/Neurológico:** Interconsulta con Cardiología/Neurología. Optimizar TA, control de arritmias, y manejo de anticoagulación.")
        
        if "EPOC" in comorb_detalles:
            st.info("🌬️ **Respiratorio:** Optimizar tratamiento broncodilatador, cese tabáquico, fisioterapia respiratoria.")
        
        if "IRC" in comorb_detalles:
            st.info("🩸 **Renal:** Control de electrolitos y función renal. Evitar nefrotóxicos.")
        
        if "Hepatopatía" in comorb_detalles:
            st.info("💊 **Hepatopatía:** Control estricto de la coagulación y valoración nutricional profunda.")
        
        plan_generado = True

    # 3. Optimización de Fragilidad y Nutrición (V9, V1, V2)
    if p_fragilidad or p_edad or p_residencia or p_cognitivo:
        st.header("3️⃣ Fragilidad y Estado Funcional (V9/V5)")
        st.info("Programa de prehabilitación multimodal: Nutrición, Ejercicio y Soporte Social/Cognitivo.")
        
        # Nutrición
        if "Pérdida Peso >5%" in frag_detalles:
            st.info("🍎 **Nutrición:** Evaluación por Nutrición. Suplementos proteicos orales (SNO) e hipercalóricos para revertir malnutrición.")
        else:
            st.info("🍎 **Nutrición Básica:** Suplementación proteica profiláctica y control de la anemia.")
            
        # Ejercicio
        if any(c in frag_detalles for c in ["Fatiga", "Resistencia (Escaleras)", "Deambulación"]):
            st.info("🏃 **Ejercicio:** Fisioterapia individualizada. Programa supervisado de ejercicio aeróbico y entrenamiento de fuerza. Objetivo: mejorar la capacidad funcional.")
        else:
            st.info("🏃 **Ejercicio Básico:** Fomentar caminata diaria y actividad funcional moderada.")
            
        # Cognitivo/Social
        if p_cognitivo or p_residencia:
            st.info("🧠 **Neuro/Social:** Valoración cognitiva y social (Trabajo Social). Soporte para el cuidado postoperatorio y gestión de la demencia/delirium.")
            
        plan_generado = True

    if not plan_generado:
        st.header("✨ **Medidas Generales**")
        st.success("Paciente de bajo riesgo. Fomentar cese de tabaco/alcohol y educación preoperatoria estándar.")
