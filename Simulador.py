import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Definición de la fórmula Logit y Probabilidad
def calculate_logit(score):
    # L = -3.844 + 0.285 * Score Total
    return -3.844 + (0.285 * score)

def calculate_probability(score):
    logit = calculate_logit(score)
    # P = 1 / (1 + e^(-L))
    return 1 / (1 + np.exp(-logit))

# Rango completo del Score (0 a 20)
scores_range = np.arange(0, 20.1, 0.1)

# --- CORRECCIÓN AQUÍ: Convertir a np.array ---
# Antes era una lista, ahora es un array de NumPy que permite comparaciones como ">= 50"
probabilities_range = np.array([calculate_probability(s) * 100 for s in scores_range])

# Puntos clave para la tabla
key_scores = [0, 5, 10, 14, 20]
key_probs = [calculate_probability(s) * 100 for s in key_scores]

# Configuración estética
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'Segoe UI' # Asegúrate de tener esta fuente o cambia a 'sans-serif'
plt.rcParams['figure.dpi'] = 150

plt.figure(figsize=(10, 6))

# Dibujar la curva completa
plt.plot(scores_range, probabilities_range, color=sns.color_palette("rocket")[2], lw=3, label='Riesgo Predicho')

# Marcar los puntos clave con anotaciones
for score, prob in zip(key_scores, key_probs):
    plt.scatter(score, prob, color='black', s=80, zorder=5)
    plt.annotate(f'{prob:.1f}%', 
                 (score + 0.5, prob + (2 if score < 14 else -5)), 
                 fontsize=10, 
                 weight='bold',
                 color='black')

# Línea del 50% (Umbral estadístico)
plt.axhline(50, color='red', linestyle='--', linewidth=1.5, label='Umbral del 50%')

# Área de alto riesgo (> 50%)
# Ahora esto funcionará porque probabilities_range es un array de numpy
plt.fill_between(scores_range, probabilities_range, 50, where=(probabilities_range >= 50), 
                 color='red', alpha=0.1, interpolate=True)

plt.title('Progresión del Riesgo de Mortalidad CriSTAL Score Modificado', fontsize=16, weight='bold')
plt.xlabel('Score Total (Puntos de Riesgo)', fontsize=14)
plt.ylabel('Probabilidad de Muerte a 30 días (%)', fontsize=14)
plt.xlim(0, 20)
plt.ylim(0, 100)
plt.xticks(np.arange(0, 21, 2))
plt.yticks(np.arange(0, 101, 10))
plt.legend(loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show() 
# Si estás en un script local y quieres guardar:
# plt.savefig("cristal_score_progression_curve.png")
