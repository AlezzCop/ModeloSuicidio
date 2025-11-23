"""
Script para generar datos de ejemplo para probar el modelo.

Genera un archivo Excel con datos sintéticos de Oaxaca que siguen
un patrón realista para probar el modelo de dinámica poblacional del suicidio.
"""

import pandas as pd
import numpy as np

# Configurar semilla para reproducibilidad
np.random.seed(42)

# Generar años
años = list(range(2010, 2021))
n_años = len(años)

# Población base creciente
poblacion_base = 2_500_000
tasa_crecimiento = 0.012  # 1.2% anual

# Generar población vulnerable (≥ 10 años)
poblacion = []
for i, año in enumerate(años):
    P = poblacion_base * (1 + tasa_crecimiento) ** i
    # Añadir algo de ruido
    P += np.random.normal(0, P * 0.01)
    poblacion.append(int(P))

# Generar defunciones totales (tasa de ~0.006)
tasa_defuncion = 0.006
defunciones_totales = []
for P in poblacion:
    D = int(P * tasa_defuncion * (1 + np.random.normal(0, 0.1)))
    defunciones_totales.append(max(D, 0))

# Generar defunciones por suicidio (tasa de ~0.00006)
tasa_suicidio = 0.00006
defunciones_suicidio = []
for P in poblacion:
    Ds = int(P * tasa_suicidio * (1 + np.random.normal(0, 0.15)))
    defunciones_suicidio.append(max(Ds, 1))

# Asegurar que defunciones_suicidio <= defunciones_totales
defunciones_suicidio = [min(ds, dt) for ds, dt in zip(defunciones_suicidio, defunciones_totales)]

# Generar población en tratamiento (T_obs)
# Asumiendo que ~0.2% de P está en tratamiento, con tendencia creciente
tasa_tratamiento_inicial = 0.002
tasa_crecimiento_T = 0.05  # 5% anual

T_obs = []
for i, P in enumerate(poblacion):
    tasa_t = tasa_tratamiento_inicial * (1 + tasa_crecimiento_T) ** i
    T = P * tasa_t * (1 + np.random.normal(0, 0.12))
    T_obs.append(int(T))

# Crear DataFrame
data = {
    'anio': años,
    'Poblacion_10ymas_P': poblacion,
    'defunciones_totales': defunciones_totales,
    'defunciones_suicidio': defunciones_suicidio,
    'T_obs': T_obs
}

df = pd.DataFrame(data)

# Mostrar resumen
print("Datos de ejemplo generados:")
print(df)
print(f"\nEstadísticas:")
print(f"  Población promedio: {df['Poblacion_10ymas_P'].mean():,.0f}")
print(f"  Defunciones totales promedio: {df['defunciones_totales'].mean():,.0f}/año")
print(f"  Defunciones por suicidio promedio: {df['defunciones_suicidio'].mean():,.1f}/año")
print(f"  T_obs promedio: {df['T_obs'].mean():,.0f}")

# Guardar a Excel
archivo_salida = "datos_oaxaca.xlsx"
df.to_excel(archivo_salida, index=False, sheet_name='Datos')

print(f"\n✓ Archivo guardado como: {archivo_salida}")
