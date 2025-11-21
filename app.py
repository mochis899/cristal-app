import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="CriSTAL Detallado", page_icon="📊", layout="centered")
st.title("📊 Registro CriSTAL Detallado")

# --- CONEXIÓN ---
df_existente = pd.DataFrame()  # Inicializar siempre

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_temp = conn.read()
    if df_temp is not None and not df_temp.empty:
        df_existente = df_temp
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.info("Configura los 'Secrets' para conectar Google Sheets.")

# --- FORMULARIO ---
with st.form("entry_form", clear_on_submit=True):
    st.info("Rellene las 9 variables del estudio:")
    
    # 1. EDAD
    col1, col2 = st.columns(2)
    id_paciente = col1.text_input("ID Paciente")
    edad = col2.number_input("1. Edad", 18, 110, 75)

    # 2. RESIDENCIA
    residencia = st.checkbox("2. ¿Vive en Residencia/Asilo?")

    # 3. ESTADO FISIOLÓGICO (Requiere >=2 para puntuar 1)
    st.markdown("---")
    st.write("**3. Estado Fisiológico (Puntúa si hay ≥2 alteraciones):**")
    fisio_opts = {
        "Consciencia (GCS desc >2)": st.checkbox("Consciencia dism."),
        "TAS < 90 mmHg": st.checkbox("TAS < 90"),
        "Frec. Resp <5 o >30": st.checkbox("FR <5 o >30"),
        "Pulso <40 o >140": st.checkbox("Pulso <40 o >140"),
        "O2 <90% / Supl": st.checkbox("SatO2 baja / O2"),
        "Hipoglucemia/Convulsión": st.checkbox("Gluc<60 / Convul."),
        "Oliguria (<15ml/h)": st.checkbox("Oliguria")
    }
    
    # 4. COMORBILIDADES (1 punto por cada una)
    st.write("**4. Comorbilidades Activas (1 pto c/u):**")
    comorb_opts = {
        "Cáncer Avanzado": st.checkbox("Cáncer Av."),
        "IRC": st.checkbox("Insuf. Renal Crón."),
        "ICC": st.checkbox("Insuf. Cardíaca"),
        "EPOC": st.checkbox("EPOC"),
        "ACV Reciente": st.checkbox("ACV Reciente"),
        "IAM Reciente": st.checkbox("IAM Reciente"),
        "Hepatopatía": st.checkbox("Hepatopatía Mod/Sev")
    }

    # 5. COGNITIVO
    st.markdown("---")
    c1, c2 = st.columns(2)
    cognitivo = c1.checkbox("5. Deterioro Cognitivo")
    
    # 6. INGRESO PREVIO
    ingreso = c2.checkbox("6. Ingreso Hosp. (último año)")
    
    # 7. PROTEINURIA
    c3, c4 = st.columns(2)
    proteinuria = c3.checkbox("7. Proteinuria")
    
    # 8. ECG ANORMAL
    ecg = c4.checkbox("8. ECG Anormal")

    # 9. FRAGILIDAD (Suma directa de items)
    st.markdown("---")
    st.write("**9. Fragilidad (Escala FRAIL - 1 pto por ítem):**")
    frag_list = st.multiselect("Seleccione ítems:", 
        ["Fatiga", "Resistencia (Escaleras)", "Deambulación", "Enfermedades >5", "Pérdida Peso >5%"])

    # --- BOTÓN Y LÓGICA ---
    submitted = st.form_submit_button("💾 Guardar Datos Detallados")

    if submitted:
        if not id_paciente.strip():
            st.error("⚠️ Debes ingresar un ID de paciente")
        else:
            # --- CÁLCULO DE PUNTOS Y VALORES (TEXTO) ---
            
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
            
            # --- PREPARAR FILA PARA EXCEL ---
            nuevo_registro = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ID": id_paciente,
                "Score_Total": score_total,
                "Prob_Mortalidad_%": prob_pct,
                # Variables Desglosadas (Valor y Puntos)
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
            
            # --- ENVIAR A GOOGLE SHEETS ---
            try:
                df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success(f"✅ Guardado: Score {score_total} (Mort: {prob_pct}%)")
                st.toast("Datos guardados correctamente")
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")
