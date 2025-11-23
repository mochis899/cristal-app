import streamlit as st
import pandas as pd
from utils import obtener_color_riesgo
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Plan de Prehabilitación", page_icon="💪", layout="wide")

st.title("💪 Plan de Prehabilitación y Optimización")
st.markdown("Esta herramienta ofrece recomendaciones de optimización preoperatoria basadas en las áreas de riesgo del paciente. Ideal para pacientes con Score CriSTAL > 8.")

# --- ENTRADA DE DATOS SIMPLIFICADA (Para fines de demostración) ---
st.subheader("1. Evaluación Rápida de Puntos de Riesgo")
st.warning("⚠️ Nota: Esta página usa datos introducidos aquí y NO los guarda en la BBDD.")

# Usamos un expander para mantener el diseño limpio
with st.expander("Seleccionar los Factores de Riesgo Activos del Paciente", expanded=True):
    
    col_v1_v3, col_v4, col_v9 = st.columns(3)
    
    # V1/V2/V3 - Fisiológico
    with col_v1_v3:
        st.markdown("#### Fisiológico y Edad")
        p_edad = st.checkbox("Edad > 65 años (+1)", key="p_edad")
        p_residencia = st.checkbox("Residencia/Asilo (+1)", key="p_residencia")
        p_fisiologico = st.checkbox("≥2 Alteraciones Fisiológicas (+1)", key="p_fisiologico")
        p_otros = st.checkbox("ECG Anormal, Proteinuria, etc. (+1 a +3)", key="p_otros")
        
    # V4 - Comorbilidades
    with col_v4:
        st.markdown("#### Comorbilidades (V4)")
        p_comorb = st.multiselect(
            "Selecciona Comorbilidades Activas (1 pto c/u)", 
            ["Cáncer Av.", "IRC", "ICC", "EPOC", "ACV Reciente", "IAM Reciente", "Hepatopatía"]
        )
        
    # V9 - Fragilidad
    with col_v9:
        st.markdown("#### Fragilidad (V9)")
        p_fragilidad = st.multiselect(
            "Selecciona Síntomas de Fragilidad (1 pto c/u)", 
            ["Fatiga", "Resistencia (Escaleras)", "Deambulación", "Enfermedades >5", "Pérdida Peso >5%"]
        )

# --- CÁLCULO DEL SCORE ---
score_total = (
    (1 if p_edad else 0) +
    (1 if p_residencia else 0) +
    (1 if p_fisiologico else 0) +
    (1 if p_otros else 0) +
    len(p_comorb) +
    len(p_fragilidad)
)

score_final = min(score_total, 20)
color_final = obtener_color_riesgo(score_final)

st.markdown("---")

# --- RESUMEN Y PLAN ---

col_resumen, col_plan = st.columns([1, 2])

# Columna de Resumen
with col_resumen:
    st.markdown("#### Score Resumen")
    st.markdown(
        f"""
        <div style="background-color:{color_final}15; border: 2px solid {color_final}; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px;">
            <p style="color: {color_final}; margin:0; font-size: 1.1em; font-weight:bold;">SCORE TOTAL</p>
            <h1 style="color: {color_final}; margin: 5px 0 10px 0; font-size: 3em;">{score_final}</h1>
        </div>
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
    
    # 1. Optimización Fisiológica Aguda (V3)
    if p_fisiologico:
        st.header("1️⃣ Fisiología Aguda (V3)")
        st.error("🚨 **¡NO OPERAR!** Tratar estas alteraciones antes de cualquier cirugía electiva.")
        st.write("""
        * **Objetivo:** Estabilizar TA, FR, Pulso y Saturación. Corregir hipoglucemia y trastornos de conciencia.
        * **Acción:** Monitorización intensiva, reanimación de fluidos si necesario, ajuste de medicación cardiológica o respiratoria.
        """)

    # 2. Optimización de Comorbilidades (V4)
    if p_comorb:
        st.header("2️⃣ Manejo de Comorbilidades (V4)")
        st.warning("Se requiere interconsulta especializada y/o intensificación del tratamiento.")
        
        if any(c in p_comorb for c in ["ICC", "IAM Reciente", "ACV Reciente"]):
             st.info("🩺 **Cardiovascular/Neurológico:** Interconsulta con Cardiología/Neurología. Control estricto de TA y anticoagulación.")
        
        if "EPOC" in p_comorb:
            st.info("🌬️ **Respiratorio:** Optimizar tratamiento inhalado, fisioterapia respiratoria. Valorar espirometría.")
        
        if "IRC" in p_comorb:
            st.info("🩸 **Renal:** Control de electrolitos y función renal. Evitar nefrotóxicos.")
        
        if "Cáncer Av." in p_comorb:
             st.info(" oncology **Oncológico:** Discutir la ventana de tiempo. Coordinar la cirugía con el tratamiento activo.")

    # 3. Optimización de Fragilidad y Nutrición (V9, V1, V2)
    if p_fragilidad or p_edad or p_residencia:
        st.header("3️⃣ Fragilidad y Estado Funcional (V9)")
        st.info("Programa de prehabilitación multimodal coordinado.")
        
        # Nutrición
        if "Pérdida Peso >5%" in p_fragilidad:
            st.info("🍎 **Nutrición:** Evaluación por Nutrición/Dietética. Suplementos proteicos orales (SNO) o enterales.")
        else:
            st.info("🍎 **Nutrición Básica:** Suplementos si no hay ingesta adecuada. Dieta rica en proteínas.")
            
        # Ejercicio
        if any(c in p_fragilidad for c in ["Fatiga", "Resistencia (Escaleras)", "Deambulación"]):
            st.info("🏃 **Ejercicio:** Fisioterapia individualizada. Ejercicio aeróbico moderado y entrenamiento de fuerza (si es seguro).")
        else:
            st.info("🏃 **Ejercicio Básico:** Fomentar caminata diaria y actividad funcional.")
            
        # Cognitivo
        if st.session_state.get('p_otros', False):
            st.info("🧠 **Neurocognitivo:** Valoración cognitiva y social. Terapia ocupacional si es necesario.")
            
        # Manejo Social
        if p_residencia:
            st.info("🏠 **Soporte Social:** Coordinación con trabajo social para el alta y seguimiento en casa o residencia.")

    if score_final < 5:
        st.header("✨ **Medidas Generales**")
        st.success("Educación al paciente, cese de tabaco/alcohol, y ayuno preoperatorio estándar.")
