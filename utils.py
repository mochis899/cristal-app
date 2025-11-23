import numpy as np
import pandas as pd
import random

# --- FUNCIONES DE CÁLCULO CÁLCULO CRIStAL ---

def calcular_probabilidad_math(score):
    """
    Calcula la probabilidad de mortalidad a 30 días usando la fórmula logit de CriSTAL.
    L = -3.844 + 0.285 * Score
    P = 1 / (1 + exp(-L))
    """
    # L = -3.844 + 0.285 * Score
    logit = -3.844 + (0.285 * score)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color_riesgo(score):
    """Asigna un color basado en el rango de riesgo del score CriSTAL."""
    if score < 8: return "#2ecc71"   # Verde (Bajo)
    elif score < 12: return "#f1c40f" # Amarillo (Intermedio)
    elif score < 14: return "#e67e22" # Naranja (Alto)
    else: return "#e74c3c"            # Rojo (Crítico)

def categorizar_score(score):
    """Asigna la categoría de riesgo basada en el score CriSTAL."""
    if score < 8: return "1. Bajo (<8)"
    elif score < 12: return "2. Intermedio (8-11)"
    elif score < 14: return "3. Alto (12-13)"
    else: return "4. Crítico (>13)"

# --- FUNCIÓN DE DATOS SIMULADOS PARA DASHBOARD ---

def get_mock_patient_data():
    """
    Genera un DataFrame con datos simulados de pacientes para el Dashboard.
    Estos datos simulan la información registrada.
    """
    N = 100  # Número de pacientes simulados
    
    # 1. Scores y Probabilidad
    scores = np.random.normal(loc=9, scale=3, size=N).clip(0, 20).astype(int)
    probabilidades = calcular_probabilidad_math(scores)
    categorias = [categorizar_score(s) for s in scores]
    
    # 2. Factores de Riesgo (Booleano)
    factores = {
        'Edad_65+': np.random.choice([True, False], N, p=[0.7, 0.3]),
        'Fragilidad': np.random.choice([True, False], N, p=[0.6, 0.4]),
        'Comorbilidad_ICC': np.random.choice([True, False], N, p=[0.3, 0.7]),
        'Comorbilidad_EPOC': np.random.choice([True, False], N, p=[0.25, 0.75]),
        'Fisiologico_Agudo': np.random.choice([True, False], N, p=[0.05, 0.95]), # Raro, solo en urgencias
        'Deterioro_Cognitivo': np.random.choice([True, False], N, p=[0.15, 0.85]),
    }

    # 3. Datos generales
    data = {
        'ID_Paciente': [f'P{i:03d}' for i in range(1, N + 1)],
        'Fecha_Registro': pd.to_datetime(pd.date_range('2024-01-01', periods=N, freq='D')),
        'Score_CriSTAL': scores,
        'Prob_Mortalidad': probabilidades,
        'Categoria_Riesgo': categorias,
        'Color': [obtener_color_riesgo(s) for s in scores],
        **factores
    }
    
    df = pd.DataFrame(data)
    
    # Añadir un Score total calculado de factores (para coherencia)
    df['Total_Factores'] = (
        df['Edad_65+'].astype(int) + 
        df['Fragilidad'].astype(int) + 
        df['Comorbilidad_ICC'].astype(int) + 
        df['Comorbilidad_EPOC'].astype(int) + 
        df['Fisiologico_Agudo'].astype(int) + 
        df['Deterioro_Cognitivo'].astype(int)
    )
    
    return df
