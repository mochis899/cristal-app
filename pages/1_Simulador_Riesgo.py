import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils import calcular_probabilidad_math, obtener_color_riesgo

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Calculadora CriSTAL", page_icon="🧮", layout="wide")

# Inicializar o recuperar el estado de la sesión
if 'current_score' not in st.session_state:
    st.session_state['current_score'] = 10 # Valor por defecto
if 'current_factors' not in st.session_state:
    st.session_state['current_factors'] = {}

# Configuración estética de la gráfica
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# --- 2. INTERFAZ Y CÁLCULO ---
st.title("🧮 Calculadora CriSTAL Interactivo")
st.markdown("Marca los factores de riesgo del paciente. El Score y el gráfico se actualizan automáticamente.")

# Contenedor para la entrada de factores
with st.container(border=True):
    col_v1_v3, col_v4, col_v9 = st.columns(3)
    
    puntos = 0
    factores = {}
    
    # --- Columna 1: Fisiológico y Edad ---
    with col_v1_v3:
        st.markdown("#### I. Edad y Fisiología")
        
        # V1. Edad
        edad = st.number_input("Edad del Paciente", 18, 110, 75)
        p_edad = 1 if edad > 65 else 0
        puntos += p_edad; factores['p_edad'] = p_edad
        st.markdown(f"*(Edad > 65 = +{p_edad} pto)*")

        # V2. Residencia
        p_residencia = st.checkbox("Vive en Residencia/Asilo (+1)", key="p_residencia")
        puntos += (1 if p_residencia else 0); factores['p_residencia'] = p_residencia
        
        # V3. Fisiológico (≥2 alteraciones)
        st.markdown("##### Alteraciones Fisiológicas (V3)")
        fisio_opts = {
            "Consciencia dism. (GCS)": st.checkbox("GCS desc >2", key="f_gcs"),
            "TAS < 90 mmHg": st.checkbox("TAS < 90", key="f_tas"),
            "Frec. Resp <5 o >30": st.checkbox("FR <5 o >30", key="f_fr"),
            "Pulso <40 o >140": st.checkbox("Pulso <40 o >140", key="f_pulso"),
            "O2 <90% / Supl": st.checkbox("SatO2 baja / O2", key="f_o2"),
            "Hipoglucemia/Convulsión": st.checkbox("Gluc<60 / Convul.", key="f_glu"),
            "Oliguria (<15ml/h)": st.checkbox("Oliguria", key="f_oligo")
        }
        num_fisio_activas = sum(fisio_opts.values())
        p_fisiologico = 1 if num_fisio_activas >= 2 else 0
        puntos += p_fisiologico; factores['p_fisiologico'] = p_fisiologico
        st.markdown(f"*(≥2 activas = +{p_fisiologico} pto)*")

    # --- Columna 2: Comorbilidades y Otros ---
    with col_v4:
        st.markdown("#### II. Comorbilidades (V4 a V8)")
        
        # V4. Comorbilidades Graves
        st.markdown("##### Patologías Crónicas (1 pto c/u)")
        comorb_opts = {
            "Cáncer Avanzado": st.checkbox("Cáncer Av. (+1)", key="c_cancer"),
            "IRC": st.checkbox("Insuf. Renal Crón. (+1)", key="c_irc"),
            "ICC": st.checkbox("Insuf. Cardíaca (+1)", key="c_icc"),
            "EPOC": st.checkbox("EPOC (+1)", key="c_epoc"),
            "ACV Reciente": st.checkbox("ACV Reciente (+1)", key="c_acv"),
            "IAM Reciente": st.checkbox("IAM Reciente (+1)", key="c_iam"),
            "Hepatopatía": st.checkbox("Hepatopatía Mod/Sev (+1)", key="c_hepato")
        }
        p_comorb = sum(comorb_opts.values())
        puntos += p_comorb; factores['p_comorb'] = p_comorb; factores['comorb_detalles'] = [k for k, v in comorb_opts.items() if v]
        st.markdown(f"*(Total V4: +{p_comorb} pto(s))*")

        # V5-V8. Otros Factores (+1 pto c/u)
        st.markdown("---")
        p_cognitivo = st.checkbox("Deterioro Cognitivo (V5) (+1)", key="p_cognitivo")
        p_ingreso = st.checkbox("Ingreso Hosp. (último año) (V6) (+1)", key="p_ingreso")
        p_proteinuria = st.checkbox("Proteinuria (V7) (+1)", key="p_proteinuria")
        p_ecg = st.checkbox("ECG Anormal (V8) (+1)", key="p_ecg")
        
        puntos += (1 if p_cognitivo else 0)
        puntos += (1 if p_ingreso else 0)
        puntos += (1 if p_proteinuria else 0)
        puntos += (1 if p_ecg else 0)
        
        factores['p_cognitivo'] = p_cognitivo
        factores['p_ingreso'] = p_ingreso
        factores['p_proteinuria'] = p_proteinuria
        factores['p_ecg'] = p_ecg
        
    # --- Columna 3: Fragilidad ---
    with col_v9:
        st.markdown("#### III. Fragilidad (V9)")
        frag_list = st.multiselect(
            "Selecciona Síntomas de Fragilidad (FRAIL - 1 pto c/u)", 
            ["Fatiga", "Resistencia (Escaleras)", "Deambulación", "Enfermedades >5", "Pérdida Peso >5%"],
            key="v9_fragilidad"
        )
        p_fragilidad = len(frag_list)
        puntos += p_fragilidad; factores['p_fragilidad'] = p_fragilidad; factores['frag_detalles'] = frag_list
        st.markdown(f"*(Total V9: +{p_fragilidad} pto(s))*")

# --- 3. RESULTADO Y ESTADO DE SESIÓN ---
score_final = min(puntos, 20)

# 💾 Guardar el score y los factores en el estado de sesión para otras páginas
st.session_state['current_score'] = score_final
st.session_state['current_factors'] = factores 

prob_final = round(calcular_probabilidad_math(score_final), 1)
color_actual = obtener_color_riesgo(score_final)

st.markdown("---")

# --- 4. VISUALIZACIÓN DE RESULTADOS Y GRÁFICO ---
col_score, col_prob = st.columns([1, 2])

with col_score:
    st.subheader("Puntuación Obtenida")
    st.metric("Score CriSTAL Total", f"**{score_final}** puntos / 20")
    
    st.markdown(f"""
    <div style="background-color:{color_actual}20; border:2px solid {color_actual}; border-radius:5px; padding:10px; text-align:center;">
        <strong style="color:{color_actual}">Probabilidad Mortalidad (30 días)</strong>
        <h1 style="color:{color_actual}; margin:0;">{prob_final:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("⚠️ **IMPORTANTE:** Este resultado se está usando en las páginas 'Decisión Compartida' y 'Plan de Prehabilitación'.")

st.write("") # Espaciador

# --- GENERACIÓN DE LA GRÁFICA ---
fig, ax = plt.subplots(figsize=(10, 5))

# 1. Rango X y Y
x = np.arange(0, 20.1, 0.1)
y = calcular_probabilidad_math(x) 

# 2. Dibujar zonas (Fondo)
ax.axvspan(0, 8, color='#2ecc71', alpha=0.1, label='Bajo Riesgo')
ax.axvspan(8, 12, color='#f1c40f', alpha=0.1, label='Riesgo Intermedio')
ax.axvspan(12, 14, color='#e67e22', alpha=0.1, label='Riesgo Alto')
ax.axvspan(14, 20, color='#e74c3c', alpha=0.1, label='Riesgo Crítico')

# 3. Dibujar curva
ax.plot(x, y, color='black', alpha=0.6, linewidth=2)

# 4. PUNTO DEL PACIENTE (Grande y visible)
ax.scatter(score_final, prob_final, s=300, color=color_actual, edgecolors='black', zorder=10)

# 5. Líneas guía
ax.axvline(score_final, color=color_actual, linestyle='--', ymax=prob_final/100)
ax.axhline(prob_final, color=color_actual, linestyle='--', xmax=score_final/20)

# Ajustes finales
ax.set_xlim(0, 20)
ax.set_ylim(0, 100)
ax.set_xlabel("Score Total (Puntos)", fontweight='bold')
ax.set_ylabel("Probabilidad (%)", fontweight='bold')
ax.set_title("Curva de Riesgo CriSTAL", fontsize=16)
ax.grid(True, linestyle=':', alpha=0.5)

with col_prob:
    st.pyplot(fig)
