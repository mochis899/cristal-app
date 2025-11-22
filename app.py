import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import base64

# --- LIBRERÍAS DE CONEXIÓN GSPREAD ---
import gspread
from google.oauth2.service_account import Credentials
# ------------------------------------

st.set_page_config(page_title="CriSTAL Secuencial", page_icon="🔢", layout="centered")
st.title("📊 Registro CriSTAL Score Modificado")


# --- INICIALIZACIÓN DE LA CONEXIÓN CON GSPREAD (CON BASE64) ---
ws = None
conn_exitosa = False

try:
    # 1. Obtener la cadena Base64 del secrets
    base64_string = st.secrets["gcp"]["service_account_base64"]
    
    # 2. Decodificar la cadena Base64 a bytes y luego a JSON (diccionario de Python)
    # 🚨 ESTE ES EL PASO CRÍTICO QUE BYPASSEA EL ERROR DE FORMATO TOML
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
    
    # 5. Lectura de datos existentes 
    df_existente = pd.DataFrame(ws.get_all_records()) 
    conn_exitosa = True
    
except Exception as e:
    # En caso de error, muestra el error de conexión
    st.error(f"⚠️ No se pudo conectar a Google Sheets. Los datos no se guardarán. Error: {e}")
    df_existente = pd.DataFrame()
    conn_exitosa = False

# -----------------------------------------------------------------------
# --- FORMULARIO (Se mantiene igual que antes) ---
# -----------------------------------------------------------------------

with st.form("entry_form", clear_on_submit=True):
    id_paciente = st.text_input("ID Paciente / Historia Clínica")
    
    # ----------------------------------------------------
    st.subheader("Datos Básicos")
    
    # 1. EDAD (V1)
    edad = st.number_input("**1. Edad** (Puntúa 1 si >65 años)", 18, 110, 75)

    # 2. RESIDENCIA (V2)
    residencia = st.checkbox("**2. ¿Vive en Residencia/Asilo? (+1 pto)**")
    
    # ----------------------------------------------------
    st.subheader("Estado Fisiológico")
    
    # 3. ESTADO FISIOLÓGICO (V3)
    st.write("**3. Alteraciones Fisiológicas (Puntúa 1 si hay ≥2 alteraciones):**")
    fisio_opts = {
        "Consciencia (GCS desc >2)": st.checkbox("Consciencia dism. (GCS)"),
        "TAS < 90 mmHg": st.checkbox("TAS < 90"),
        "Frec. Resp <5 o >30": st.checkbox("FR <5 o >30"),
        "Pulso <40 o >140": st.checkbox("Pulso <40 o >140"),
        "O2 <90% / Supl": st.checkbox("SatO2 baja / O2"),
        "Hipoglucemia/Convulsión": st.checkbox("Gluc<60 / Convul."),
        "Oliguria (<15ml/h)": st.checkbox("Oliguria")
    }
    
    # ----------------------------------------------------
    st.subheader("Comorbilidades Crónicas")

    # 4. COMORBILIDADES GRAVES (V4)
    st.write("**4. Patologías Crónicas (1 pto c/u):**")
    comorb_opts = {
        "Cáncer Avanzado": st.checkbox("Cáncer Av."),
        "IRC": st.checkbox("Insuf. Renal Crón."),
        "ICC": st.checkbox("Insuf. Cardíaca"),
        "EPOC": st.checkbox("EPOC"),
        "ACV Reciente": st.checkbox("ACV Reciente"),
        "IAM Reciente": st.checkbox("IAM Reciente"),
        "Hepatopatía": st.checkbox("Hepatopatía Mod/Sev")
    }
    
    st.markdown("---")
    st.write("**Otras Comorbilidades/Factores:**")
    c1, c2 = st.columns(2)
    
    # 5. DETERIORO COGNITIVO (V5)
    cognitivo = c1.checkbox("**5. Deterioro Cognitivo (+1 pto)**")
    # 6. INGRESO PREVIO (V6)
    ingreso = c2.checkbox("**6. Ingreso Hosp. (último año) (+1 pto)**")
    
    # 7. PROTEINURIA (V7)
    proteinuria = c1.checkbox("**7. Proteinuria (+1 pto)**")
    # 8. ECG ANORMAL (V8)
    ecg = c2.checkbox("**8. ECG Anormal (+1 pto)**")

    # ----------------------------------------------------
    st.subheader("Fragilidad") 

    # 9. FRAGILIDAD (V9)
    st.write("**9. Fragilidad (Escala FRAIL - 1 pto por ítem positivo):**")
    frag_list = st.multiselect("Seleccione ítems positivos:", 
        ["Fatiga", "Resistencia (Escaleras)", "Deambulación", "Enfermedades >5", "Pérdida Peso >5%"])

    # --- BOTÓN Y LÓGICA ---
    submitted = st.form_submit_button("💾 Guardar Datos Detallados")

    if submitted and id_paciente:
        
        # --- CÁLCULO DE PUNTOS Y VALORES (V1 a V9) ---
        
        # V1: Edad
        v1_val = edad
        v1_pts = 1 if edad > 65 else 0
        
        # V2: Residencia
        v2_val = "Sí" if residencia else "No"
        v2_pts = 1 if residencia else 0
        
        # V3: Fisiológico (Lógica especial: >=2 items = 1 punto, sino 0)
        fisio_activas = [k for k, v in fisio_opts.items() if v]
        v3_val = ", ".join(fisio_activas) if fisio_activas else "Ninguna"
        v3_pts = 1 if len(fisio_activas) >= 2 else 0
        
        # V4: Comorbilidades (Suma directa)
        comorb_activas = [k for k, v in comorb_opts.items() if v]
        v4_val = ", ".join(comorb_activas) if comorb_activas else "Ninguna"
        v4_pts = len(comorb_activas)
        
        # V5, V6, V7, V8 (Simples)
        v5_val = "Sí" if cognitivo else "No"
        v5_pts = 1 if cognitivo else 0
        
        v6_val = "Sí" if ingreso else "No"
        v6_pts = 1 if ingreso else 0
        
        v7_val = "Sí" if proteinuria else "No"
        v7_pts = 1 if proteinuria else 0
        
        v8_val = "Sí" if ecg else "No"
        v8_pts = 1 if ecg else 0
        
        # V9: Fragilidad
        v9_val = ", ".join(frag_list) if frag_list else "No Frágil"
        v9_pts = len(frag_list)

        # --- SCORE TOTAL Y PROBABILIDAD ---
        score_total = v1_pts + v2_pts + v3_pts + v4_pts + v5_pts + v6_pts + v7_pts + v8_pts + v9_pts
        
        # Fórmula Logística Tesis
        logit = -3.844 + (0.285 * score_total)
        prob = 1 / (1 + np.exp(-logit))
        prob_pct = round(prob * 100, 2)
        
        # --- MOSTRAR RESULTADOS INMEDIATOS ---
        st.success(f"✅ Paciente **{id_paciente}** guardado correctamente.")
        col_s, col_p = st.columns(2)
        col_s.metric("Score CriSTAL Total", f"{score_total} puntos")
        col_p.metric("Mortalidad Est. (30 días)", f"{prob_pct}%")
        
        # --- PREPARAR FILA PARA EXCEL ---
        nuevo_registro = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ID": id_paciente,
            "Score_Total": score_total,
            "Prob_Mortalidad_%": prob_pct,
            "V1_Edad_Valor": v1_val, "V1_Edad_Puntos": v1_pts,
            "V2_Residencia_Valor": v2_val, "V2_Residencia_Puntos": v2_pts,
            "V3_Fisiologico_Detalle": v3_val, "V3_Fisiologico_Puntos": v3_pts,
            "V4_Comorbilidad_Detalle": v4_val, "V4_Comorbilidad_Puntos": v4_pts,
            "V5_Cognitivo_Detalle": v5_val, "V5_Cognitivo_Puntos": v5_pts,
            "V6_IngresoPrevio_Valor": v6_val, "V6_IngresoPrevio_Puntos": v6_pts,
            "V7_Proteinuria_Valor": v7_val, "V7_Proteinuria_Puntos": v7_pts,
            "V8_ECG_Valor": v8_val, "V8_ECG_Puntos": v8_pts,
            "V9_Fragilidad_Detalle": v9_val, "V9_Fragilidad_Puntos": v9_pts
        }])
        
        # --- ENVIAR A GOOGLE SHEETS (USANDO GSPREAD) ---
        if conn_exitosa and ws is not None:
            try:
                datos_fila = nuevo_registro.values.tolist()
                ws.append_rows(datos_fila, value_input_option='USER_ENTERED')
                st.toast("Datos guardados en la nube correctamente")
            except Exception as e:
                st.error(f"Error al guardar en la nube: {e}")
        else:
            st.warning("⚠️ El cálculo fue exitoso, pero la conexión a Google Sheets falló. Los datos no se han guardado.")
