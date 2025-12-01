import pandas as pd
import numpy as np

# Generar datos sintéticos para prueba
anios = np.arange(2010, 2021)
n = len(anios)

# P(t) creciente
P = np.linspace(3000000, 3500000, n)

# Defunciones totales (aprox 0.6% de P)
def_tot = P * 0.006 + np.random.normal(0, 100, n)

# Defunciones suicidio (aprox 0.01% de P)
def_sui = P * 0.0001 + np.random.normal(0, 10, n)

# T_obs (población en tratamiento, aprox 0.5% de P)
T_obs = P * 0.005 + np.random.normal(0, 500, n)

df = pd.DataFrame({
    'anio': anios,
    'Poblacion_10ymas_P': P,
    'defunciones_totales': def_tot,
    'defunciones_suicidio': def_sui,
    'T_obs': T_obs
})

df.to_excel('Simulacion.xlsx', sheet_name='Datos', index=False)
print("Simulacion.xlsx generado.")
