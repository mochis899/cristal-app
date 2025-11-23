import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import base64

# Importamos la función de cálculo del motor
from utils import calcular_probabilidad_math, obtener_color_riesgo

# --- LIBRERÍAS DE CONEXIÓN GSPREAD ---
import gspread
from google.oauth2.service_account import Credentials
# ------------------------------------

# Configuración de la página principal
st.set_page_config(page_title="CriSTAL: Registro de Paciente", page_icon="🔢", layout="centered")
st.title("📝 CriSTAL: Registro de Paciente")
st.markdown("Fórmula Logística: L = -3.844 + 0.285 * Score")

# --- INICIALIZACIÓN DE LA CONEXIÓN CON GSPREAD (CON BASE64) ---
ws = None
conn_exitosa = False

try:
    # 1. Obtener la cadena Base64 de Streamlit Secrets
    # Nota: Asume que tienes st.secrets["gcp"]["service_account_base64"]
    base64_string = st.secrets["gcp"]["service_account_base64"]
    
    # 2. Decodificar la cadena Base64 a JSON
    json_service_account = base64.b64decode(base64_string).decode('utf-8')
    service_account_info = json.loads(json_service_account)
    
    # 3. Preparar credenciales
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes
    )
    
    # 4. Autorización y conexión
    gc = gspread.authorize(credentials)
    
    SPREADSHEET_ID = st.secrets["gcp"]["spreadsheet_id"]
    WORKSHEET_NAME = st.secrets["gcp"]["worksheet_name"] 
    
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(WORKSHEET_NAME) 
    
    # Lectura de datos existentes no es necesaria aquí, pero se deja el flag
    conn_exitosa = True
    st.sidebar.success("Conexión a BBDD Exitosa")
    
except Exception as e:
    # Usamos st.sidebar para no saturar la pantalla principal con el error
    st.sidebar.error(f"⚠️ Error BBDD. No se pudo conectar a Google Sheets: {e}")
    conn_exitosa = False

# -----------------------------------------------------------------------
# --- FORMULARIO ---
# -----------------------------------------------------------------------

with st.form("entry_form", clear_on_submit=True):
    id_paciente = st.text_input("ID Paciente / Historia Clínica", key="id_input")
    
    puntos = 0
    data_to_save = {}

    # --- PANELES DEL FORMULARIO ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("I. Datos y Fisiología")
        
        # 1. EDAD (V1)
        edad = st.number_input("**1. Edad**", 18, 110, 75)
        v1_val = edad; v1_pts = 1 if edad > 65 else 0
        if v1_pts == 1: st.markdown("*(+1 pto)*")
        puntos += v1_pts

        # 2. RESIDENCIA (V2)
        residencia = st.checkbox("**2. ¿Vive en Residencia/Asilo?**")
        v2_val = "Sí" if residencia else "No"; v2_pts = 1 if residencia else 0
        if v2_pts == 1: st.markdown("*(+1 pto)*")
        puntos += v2_pts
        
        # 3. ESTADO FISIOLÓGICO (V3)
        st.write("**3. Alteraciones Fisiológicas (≥2 = +1 pto):**")
        fisio_opts = {
            "Consciencia dism. (GCS)": st.checkbox("GCS desc >2"),
            "TAS < 90 mmHg": st.checkbox("TAS < 90"),
            "Frec. Resp <5 o >30": st.checkbox("FR <5 o >30"),
            "Pulso <40 o >140": st.checkbox("Pulso <40 o >140"),
            "O2 <90% / Supl": st.checkbox("SatO2 baja / O2"),
            "Hipoglucemia/Convulsión": st.checkbox("Gluc<60 / Convul."),
            "Oliguria (<15ml/h)": st.checkbox("Oliguria")
        }
        fisio_activas = [k for k, v in fisio_opts.items() if v]
        v3_val = ", ".join(fisio_activas) if fisio_activas else "Ninguna"
        v3_pts = 1 if len(fisio_activas) >= 2 else 0
        if v3_pts == 1: st.markdown("*(+1 pto)*")
        puntos += v3_pts

    with col2:
        st.subheader("II. Comorbilidades y Factores")

        # 4. COMORBILIDADES GRAVES (V4)
        st.write("**4. Patologías Crónicas (Puntúa 1 pto c/u):**")
        comorb_opts = {
            "Cáncer Avanzado": st.checkbox("Cáncer Av. (+1)"),
            "IRC": st.checkbox("Insuf. Renal Crón. (+1)"),
            "ICC": st.checkbox("Insuf. Cardíaca (+1)"),
            "EPOC": st.checkbox("EPOC (+1)"),
            "ACV Reciente": st.checkbox("ACV Reciente (+1)"),
            "IAM Reciente": st.checkbox("IAM Reciente (+1)"),
            "Hepatopatía": st.checkbox("Hepatopatía Mod/Sev (+1)")
        }
        comorb_activas = [k for k, v in comorb_opts.items() if v]
        v4_val = ", ".join(comorb_activas) if comorb_activas else "Ninguna"
        v4_pts = len(comorb_activas)
        st.markdown(f"*(Total: +{v4_pts} pto(s))*")
        puntos += v4_pts

        # 5 a 8. OTROS FACTORES
        st.markdown("---")
        st.write("**Otros Factores (+1 pto c/u):**")
        
        # V5. COGNITIVO
        cognitivo = st.checkbox("**5. Deterioro Cognitivo** (+1)")
        v5_val = "Sí" if cognitivo else "No"; v5_pts = 1 if cognitivo else 0
        puntos += v5_pts
        
        # V6. INGRESO PREVIO
        ingreso = st.checkbox("**6. Ingreso Hosp. (último año)** (+1)")
        v6_val = "Sí" if ingreso else "No"; v6_pts = 1 if ingreso else 0
        puntos += v6_pts
        
        # V7. PROTEINURIA
        proteinuria = st.checkbox("**7. Proteinuria** (+1)")
        v7_val = "Sí" if proteinuria else "No"; v7_pts = 1 if proteinuria else 0
        puntos += v7_pts
        
        # V8. ECG ANORMAL
        ecg = st.checkbox("**8. ECG Anormal** (+1)")
        v8_val = "Sí" if ecg else "No"; v8_pts = 1 if ecg else 0
        puntos += v8_pts
        
        # 9. FRAGILIDAD (V9)
        st.markdown("---")
        st.subheader("III. Fragilidad")
        frag_list = st.multiselect("**9. Fragilidad (FRAIL - 1 pto c/u):**", 
            ["Fatiga", "Resistencia (Escaleras)", "Deambulación", "Enfermedades >5", "Pérdida Peso >5%"])
        v9_val = ", ".join(frag_list) if frag_list else "No Frágil"
        v9_pts = len(frag_list)
        st.markdown(f"*(Total: +{v9_pts} pto(s))*")
        puntos += v9_pts

    # --- BOTÓN DE ENVÍO ---
    submitted = st.form_submit_button("💾 Calcular y Guardar Registro")

    if submitted:
        if not id_paciente:
            st.error("Por favor, introduce el ID del Paciente para guardar el registro.")
        else:
            score_total = min(puntos, 20)
            
            # Cálculo usando la función robusta de utils.py
            prob_math_pct = round(calcular_probabilidad_math(score_total), 2)
            
            # Prepara el DataFrame para guardar
            nuevo_registro = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ID": id_paciente,
                "Score_Total": score_total,
                "Prob_Mortalidad_Mat_%": prob_math_pct, 
                "V1_Edad_Valor": v1_val, "V1_Edad_Puntos": v1_pts,
                "V2_Residencia_Valor": v2_val, "V2_Residencia_Puntos": v2_pts,
                "V3_Fisiologico_Detalle": v3_val, "V3_Fisiologico_Puntos": v3_pts,
                "V4_Comorbilidad_Detalle": v4_val, "V4_Comorbilidad_Puntos": v4_pts,
                "V5_Cognitivo_Detalle": v5_val, "V5_Cognitivo_Puntos": v5_pts,
                "V6_IngresoPrevio_Valor": v6_val, "V6_IngresoPrevio_Puntos": v6_pts,
                "V7_Proteinuria_Valor": v7_val, "V7_Proteinuria_Puntos": v7_pts,
                "V8_ECG_Valor": v8_val, "V8_ECG_Puntos": v8_pts,
                "V9_Fragilidad_Detalle": v9_val, "V9_Fragilidad_Puntos": v9_pts,
                "Outcome_30dias": "" # Columna para rellenar en el seguimiento
            }])
            
            # --- MOSTRAR RESULTADOS INMEDIATOS ---
            color_final = obtener_color_riesgo(score_total)
            st.success(f"✅ Registro **{id_paciente}** listo.")
            
            col_s, col_pm = st.columns(2)
            col_s.metric("Score CriSTAL Total", f"**{score_total}** puntos")
            
            col_pm.markdown(
                f"""
                <div style="background-color:{color_final}20; border: 2px solid {color_final}; border-radius: 5px; padding: 0px 10px; text-align: center;">
                    <p style="color: {color_final}; margin:0; font-weight:bold;">Mortalidad Estimada</p>
                    <h2 style="color: {color_final}; margin:0;">{prob_math_pct}%</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # --- ENVIAR A GOOGLE SHEETS ---
            if conn_exitosa and ws is not None:
                try:
                    datos_fila = nuevo_registro.values.tolist()
                    ws.append_rows(datos_fila, value_input_option='USER_ENTERED')
                    st.toast("Datos guardados en la nube correctamente")
                except Exception as e:
                    st.error(f"Error al guardar en la nube: {e}")
            else:
                st.warning("⚠️ El cálculo fue exitoso, pero la conexión a Google Sheets falló. Los datos no se han guardado.")
