import numpy as np

# --- FUNCIONES MATEMÁTICAS DEL SCORE ---

def calcular_probabilidad_math(score):
    """
    Calcula la probabilidad de mortalidad CriSTAL (Fórmula Logística Estándar).
    Esta es la interpretación matemáticamente correcta del logit.
    L = -3.844 + 0.285 * Score Total
    P = 1 / (1 + e^(-L))
    """
    logit = -3.844 + (0.285 * score)
    # np.exp funciona tanto con números simples como con arrays (vectorización)
    prob = 1 / (1 + np.exp(-logit))
    return prob * 100

def obtener_color_riesgo(score):
    """
    Devuelve un color para la visualización basado en el Score.
    """
    if score < 8: return "#2ecc71"      # Verde (Bajo)
    elif score < 12: return "#f1c40f"    # Amarillo (Intermedio)
    elif score < 14: return "#e67e22"    # Naranja (Alto)
    else: return "#e74c3c"               # Rojo (Crítico)
