import numpy as np
import pandas as pd

def estimar_tasas_defuncion(df: pd.DataFrame, anio_ini: int, anio_fin: int) -> tuple[float, float, float]:
    """
    Calcula las tasas anuales de defunción (total, suicidio, no suicidio)
    y devuelve (delta, delta_s, delta_n) como promedios en el intervalo
    [anio_ini, anio_fin].
    """
    mask = (df['anio'] >= anio_ini) & (df['anio'] <= anio_fin)
    df_subset = df.loc[mask]
    
    if df_subset.empty:
        raise ValueError(f"No hay datos en el rango {anio_ini}-{anio_fin}")

    delta = df_subset['delta_t'].mean()
    delta_s = df_subset['delta_s_t'].mean()
    delta_n = delta - delta_s
    
    return delta, delta_s, delta_n

def estimar_m(df: pd.DataFrame, anio_ini: int, anio_fin: int) -> float:
    """
    Calcula m_i = T_obs / P en el intervalo de años [anio_ini, anio_fin]
    y devuelve la media geométrica de m_i.
    """
    mask = (df['anio'] >= anio_ini) & (df['anio'] <= anio_fin)
    df_subset = df.loc[mask]
    
    if df_subset.empty:
        raise ValueError(f"No hay datos en el rango {anio_ini}-{anio_fin}")

    m_i = df_subset['T_obs'] / df_subset['Poblacion_10ymas_P']
    # Filtrar valores <= 0 para log
    m_i_valid = m_i[m_i > 0]
    
    if m_i_valid.empty:
        return 0.0
        
    m = np.exp(np.mean(np.log(m_i_valid)))
    return m

def calcular_phi_psi(m: float, phi: float = 0.5) -> tuple[float, float]:
    """
    Dado m y un valor para phi en [0,1], calcula psi = 1 - m - phi * m.
    """
    psi = 1 - m - phi * m
    if not (0 <= psi <= 1):
        print(f"Advertencia: psi calculado ({psi}) está fuera del rango [0, 1]. Revise m ({m}) y phi ({phi}).")
    return phi, psi

def construir_series_lineales(df: pd.DataFrame, m: float, phi: float, psi: float) -> pd.DataFrame:
    """
    Añade al DataFrame las columnas:
        T_lin, R_lin, S_lin,
    aplicando las relaciones lineales anteriores.
    """
    df = df.copy()
    df['T_lin'] = m * df['Poblacion_10ymas_P']
    df['R_lin'] = phi * df['T_lin']
    df['S_lin'] = df['Poblacion_10ymas_P'] - df['T_lin'] - df['R_lin']
    return df
