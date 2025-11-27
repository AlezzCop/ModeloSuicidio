import numpy as np
import pandas as pd
from .parameters import ModeloParametros
from .nonlinear_model import ModeloNoLineal

def condiciones_iniciales(df: pd.DataFrame, params: ModeloParametros, anio_ini: int) -> np.ndarray:
    """
    Calcula [S0, T0, R0] a partir del año anio_ini usando P, m, phi.
    """
    row = df[df['anio'] == anio_ini]
    if row.empty:
        raise ValueError(f"No hay datos para el año {anio_ini}")
    
    P0 = row['Poblacion_10ymas_P'].values[0]
    
    # Opción A: Usar m * P0
    T0 = params.m * P0
    
    # Opción B: Usar T_obs real si se prefiere (aquí seguimos la lógica de m * P0 para consistencia con teoría)
    # T0 = row['T_obs'].values[0]
    
    R0 = params.phi * T0
    S0 = P0 - T0 - R0
    
    return np.array([S0, T0, R0])

def prueba_escritorio(df: pd.DataFrame, params: ModeloParametros, anio_ini: int, anio_fin: int) -> pd.DataFrame:
    """
    Corre una simulación en el rango [anio_ini, anio_fin],
    compara T_model con T_obs y devuelve los errores por año.
    """
    # Preparar modelo
    anios_data = df['anio'].values
    P_data = df['Poblacion_10ymas_P'].values
    modelo = ModeloNoLineal(params, anios_data, P_data)
    
    # Condiciones iniciales
    x0 = condiciones_iniciales(df, params, anio_ini)
    
    # Simular
    # Usamos t_eval en los años enteros para comparar directamente
    anios_eval = np.arange(anio_ini, anio_fin + 1)
    
    # solve_ivp directo para obtener puntos exactos
    from scipy.integrate import solve_ivp
    sol = solve_ivp(
        fun=modelo.rhs,
        t_span=(anio_ini, anio_fin),
        y0=x0,
        t_eval=anios_eval,
        method='RK45'
    )
    
    # Construir DataFrame de resultados
    res_df = pd.DataFrame({
        'anio': sol.t,
        'S_model': sol.y[0],
        'T_model': sol.y[1],
        'R_model': sol.y[2]
    })
    
    # Merge con datos observados
    df_obs = df[['anio', 'Poblacion_10ymas_P', 'T_obs']].copy()
    merged = pd.merge(res_df, df_obs, on='anio', how='left')
    
    merged['error_abs'] = merged['T_model'] - merged['T_obs']
    merged['error_rel'] = (merged['error_abs'] / merged['T_obs']).abs()
    
    return merged
