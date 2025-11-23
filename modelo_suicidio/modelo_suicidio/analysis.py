"""
Módulo para análisis y evaluación del modelo.

Incluye funciones para calcular condiciones iniciales,
ejecutar pruebas de escritorio y comparar resultados con datos observados.
"""

import numpy as np
import pandas as pd
from typing import Tuple
from .parameters import ModeloParametros
from .model import ModeloSuicidio


def condiciones_iniciales(df: pd.DataFrame, params: ModeloParametros) -> np.ndarray:
    """
    Calcula las condiciones iniciales S0, T0, R0 a partir del primer año de datos.
    
    Usa el primer año del DataFrame como t0 y calcula:
        P0 = P(t0)
        T0 = m * P0
        R0 = φ * T0
        S0 = P0 - T0 - R0
    
    Args:
        df: DataFrame con los datos (ordenado por año)
        params: Objeto ModeloParametros con los parámetros estimados
    
    Returns:
        Array numpy [S0, T0, R0] con las condiciones iniciales
    """
    # Obtener población del primer año
    P0 = df['Poblacion_10ymas_P'].iloc[0]
    
    # Calcular T0 usando la tasa global de tratamiento
    T0 = params.m * P0
    
    # Calcular R0 usando la proporción phi
    R0 = params.phi * T0
    
    # Calcular S0 por diferencia
    S0 = P0 - T0 - R0
    
    # Validar que los valores sean no negativos
    if S0 < 0:
        print(f"⚠️  Advertencia: S0 = {S0:.2f} < 0. Ajustando a 0.")
        S0 = 0
    
    if T0 < 0:
        print(f"⚠️  Advertencia: T0 = {T0:.2f} < 0. Ajustando a 0.")
        T0 = 0
    
    if R0 < 0:
        print(f"⚠️  Advertencia: R0 = {R0:.2f} < 0. Ajustando a 0.")
        R0 = 0
    
    print(f"\nCondiciones iniciales (año {df['anio'].iloc[0]}):")
    print(f"  P0 = {P0:,.0f}")
    print(f"  S0 = {S0:,.0f} ({100*S0/P0:.2f}% de P)")
    print(f"  T0 = {T0:,.0f} ({100*T0/P0:.2f}% de P)")
    print(f"  R0 = {R0:,.0f} ({100*R0/P0:.2f}% de P)")
    print(f"  Verificación: S0+T0+R0 = {S0+T0+R0:,.0f} (≈ P0 = {P0:,.0f})")
    
    return np.array([S0, T0, R0])


def prueba_escritorio(df: pd.DataFrame, params: ModeloParametros, verbose: bool = True) -> pd.DataFrame:
    """
    Ejecuta una prueba de escritorio del modelo.
    
    Realiza los siguientes pasos:
    1. Calcula condiciones iniciales
    2. Simula el modelo en el rango de años cubierto por el DataFrame
    3. Interpola T_model(t_k) en los años de la tabla
    4. Compara T_model con T_obs
    5. Calcula métricas de error
    
    Args:
        df: DataFrame con los datos observados
        params: Objeto ModeloParametros con los parámetros
        verbose: Si True, imprime detalles del proceso
    
    Returns:
        DataFrame con columnas:
            - anio: Año
            - P: Población vulnerable
            - T_obs: T observado
            - T_model: T simulado
            - error_abs: Error absoluto (T_model - T_obs)
            - error_rel: Error relativo ((T_model - T_obs) / T_obs)
    """
    # Calcular condiciones iniciales
    if verbose:
        print("\n" + "="*60)
        print("PRUEBA DE ESCRITORIO")
        print("="*60)
    
    x0 = condiciones_iniciales(df, params)
    
    # Crear modelo
    modelo = ModeloSuicidio(params, df['Poblacion_10ymas_P'], df['anio'])
    
    # Años a simular
    t_inicial = df['anio'].iloc[0]
    t_final = df['anio'].iloc[-1]
    
    if verbose:
        print(f"\nSimulando desde año {t_inicial} hasta {t_final}...")
    
    # Evaluar en los años observados
    t_puntos = df['anio'].values.astype(float)
    S_model, T_model, R_model = modelo.evaluar_en_puntos(t_inicial, t_final, x0, t_puntos)
    
    # Crear DataFrame de resultados
    resultados = pd.DataFrame({
        'anio': df['anio'].values,
        'P': df['Poblacion_10ymas_P'].values,
        'T_obs': df['T_obs'].values,
        'T_model': T_model,
        'S_model': S_model,
        'R_model': R_model
    })
    
    # Calcular errores
    resultados['error_abs'] = resultados['T_model'] - resultados['T_obs']
    resultados['error_rel'] = resultados['error_abs'] / resultados['T_obs']
    resultados['error_rel_pct'] = resultados['error_rel'] * 100
    
    # Métricas globales
    mae = np.mean(np.abs(resultados['error_abs']))
    rmse = np.sqrt(np.mean(resultados['error_abs']**2))
    mape = np.mean(np.abs(resultados['error_rel'])) * 100  # en porcentaje
    
    if verbose:
        print("\nResultados:")
        print(f"  MAE (Error Absoluto Medio):     {mae:,.2f}")
        print(f"  RMSE (Raíz del Error Cuadrático): {rmse:,.2f}")
        print(f"  MAPE (Error Relativo Medio):    {mape:.2f}%")
        
        # Mostrar tabla resumen
        print("\nTabla de resultados (primeros y últimos 3 años):")
        print("-" * 80)
        pd.set_option('display.width', 100)
        pd.set_option('display.max_columns', None)
        
        columnas_mostrar = ['anio', 'P', 'T_obs', 'T_model', 'error_abs', 'error_rel_pct']
        
        if len(resultados) <= 6:
            print(resultados[columnas_mostrar].to_string(index=False, float_format=lambda x: f'{x:,.2f}'))
        else:
            print(resultados.head(3)[columnas_mostrar].to_string(index=False, float_format=lambda x: f'{x:,.2f}'))
            print("...")
            print(resultados.tail(3)[columnas_mostrar].to_string(index=False, float_format=lambda x: f'{x:,.2f}'))
        
        print("-" * 80)
    
    return resultados


def calcular_metricas(T_obs: np.ndarray, T_model: np.ndarray) -> dict:
    """
    Calcula métricas de error entre valores observados y modelo.
    
    Args:
        T_obs: Valores observados
        T_model: Valores del modelo
    
    Returns:
        Diccionario con métricas: MAE, RMSE, MAPE, R2
    """
    # Error absoluto
    error_abs = T_model - T_obs
    
    # Error relativo
    error_rel = error_abs / T_obs
    
    # Métricas
    mae = np.mean(np.abs(error_abs))
    rmse = np.sqrt(np.mean(error_abs**2))
    mape = np.mean(np.abs(error_rel)) * 100  # porcentaje
    
    # R^2 (coeficiente de determinación)
    ss_res = np.sum(error_abs**2)
    ss_tot = np.sum((T_obs - np.mean(T_obs))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'R2': r2
    }


def comparar_parametros(params1: ModeloParametros, params2: ModeloParametros) -> None:
    """
    Imprime una comparación lado a lado de dos conjuntos de parámetros.
    
    Útil para comparar parámetros iniciales vs calibrados.
    
    Args:
        params1: Primer conjunto de parámetros (e.g., iniciales)
        params2: Segundo conjunto de parámetros (e.g., calibrados)
    """
    print("\n" + "="*70)
    print("COMPARACIÓN DE PARÁMETROS")
    print("="*70)
    print(f"{'Parámetro':<15} {'Conjunto 1':>15} {'Conjunto 2':>15} {'Cambio %':>15}")
    print("-"*70)
    
    atributos = ['delta', 'delta_s', 'delta_n', 'm', 'phi', 'psi', 'theta', 'rho', 'beta', 'gamma']
    nombres = ['δ', 'δ_s', 'δ_n', 'm', 'φ', 'ψ', 'θ', 'ρ', 'β', 'γ']
    
    for attr, nombre in zip(atributos, nombres):
        val1 = getattr(params1, attr)
        val2 = getattr(params2, attr)
        cambio = ((val2 - val1) / val1 * 100) if val1 != 0 else 0
        print(f"{nombre:<15} {val1:>15.6f} {val2:>15.6f} {cambio:>14.2f}%")
    
    print("="*70 + "\n")
