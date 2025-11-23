# utils.py

import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# --- FUNCIONES MATEMÁTICAS ---
def calcular_probabilidad(score):
    """Calcula la probabilidad de mortalidad CriSTAL."""
    logit = -3.844 + (0.285 * score)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color_riesgo(score):
    """Devuelve un color para la visualización del riesgo."""
    if score < 8: return "#2ecc71"
    elif score < 12: return "#f1c40f"
    elif score < 14: return "#e67e22"
    else: return "#e74c3c"

# --- FUNCIONES DE CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    # Aquí va tu código para cargar credenciales de Streamlit Secrets
    # o desde un archivo JSON (si es local) y devolver el cliente de gspread
    # Ejemplo:
    # creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"],
    # scopes=["https://www.googleapis.com/auth/spreadsheets"])
    # client = gspread.authorize(creds)
    # return client
    pass # Reemplaza esto con tu lógica de conexión

def save_data_to_gsheets(data):
    """Guarda un diccionario de datos en la hoja de cálculo."""
    # client = get_gspread_client()
    # sheet = client.open("Nombre de tu Hoja de Cálculo").worksheet(0)
    # sheet.append_row(list(data.values()))
    pass # Reemplaza esto con tu lógica de guardado

