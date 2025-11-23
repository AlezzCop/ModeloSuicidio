"""
Módulo para calibración automática de parámetros del modelo.

Usa scipy.optimize.least_squares para ajustar los parámetros theta, rho, beta y gamma
minimizando la diferencia entre T_model y T_obs en los años observados.
"""

import numpy as np
import pandas as pd
from scipy.optimize import least_squares, OptimizeResult
from typing import Tuple, Optional
from .parameters import ModeloParametros
from .model import ModeloSuicidio
from .analysis import condiciones_iniciales, calcular_metricas


def calibrar_parametros(
    df: pd.DataFrame,
    params_iniciales: ModeloParametros,
    metodo: str = 'trf',
    verbose: int = 1
) -> Tuple[ModeloParametros, OptimizeResult]:
    """
    Calibra los parámetros theta, rho, beta y gamma del modelo.
    
    Usa least_squares para minimizar el error entre T_model y T_obs.
    Los parámetros básicos (delta, delta_s, delta_n, m, phi, psi) se mantienen fijos.
    
    Args:
        df: DataFrame con los datos observados
        params_iniciales: Parámetros iniciales (punto de partida)
        metodo: Método de optimización ('trf', 'dogbox', 'lm')
        verbose: Nivel de verbosidad (0=silencioso, 1=progreso, 2=detallado)
    
    Returns:
        Tupla (params_calibrados, resultado_optimizacion):
            - params_calibrados: ModeloParametros con parámetros optimizados
            - resultado_optimizacion: Objeto OptimizeResult de scipy
    """
    print("\n" + "="*60)
    print("CALIBRACIÓN DE PARÁMETROS")
    print("="*60)
    print(f"\nParámetros a calibrar: θ (theta), ρ (rho), β (beta), γ (gamma)")
    print(f"Método de optimización: {metodo}")
    print(f"Número de observaciones: {len(df)}")
    
    # Guardar parámetros fijos
    params_fijos = {
        'delta': params_iniciales.delta,
        'delta_s': params_iniciales.delta_s,
        'delta_n': params_iniciales.delta_n,
        'm': params_iniciales.m,
        'phi': params_iniciales.phi,
        'psi': params_iniciales.psi,
    }
    
    # Valores iniciales de parámetros a calibrar
    x0 = np.array([
        params_iniciales.theta,
        params_iniciales.rho,
        params_iniciales.beta,
        params_iniciales.gamma
    ])
    
    print(f"\nValores iniciales:")
    print(f"  θ (theta) = {x0[0]:.6f}")
    print(f"  ρ (rho)   = {x0[1]:.6f}")
    print(f"  β (beta)  = {x0[2]:.6f}")
    print(f"  γ (gamma) = {x0[3]:.6f}")
    
    # Datos observados
    T_obs = df['T_obs'].values
    t_puntos = df['anio'].values.astype(float)
    t_inicial = t_puntos[0]
    t_final = t_puntos[-1]
    
    # Función objetivo (residuos)
    def residuos(x: np.ndarray) -> np.ndarray:
        """
        Calcula los residuos entre T_model y T_obs.
        
        Args:
            x: Vector [theta, rho, beta, gamma]
        
        Returns:
            Vector de residuos (T_model - T_obs)
        """
        theta, rho, beta, gamma = x
        
        # Crear parámetros con valores actualizados
        params = ModeloParametros(
            **params_fijos,
            theta=theta,
            rho=rho,
            beta=beta,
            gamma=gamma
        )
        
        # Calcular condiciones iniciales
        x0_cond = condiciones_iniciales(df, params)
        
        # Crear modelo
        modelo = ModeloSuicidio(params, df['Poblacion_10ymas_P'], df['anio'])
        
        # Simular
        try:
            S_model, T_model, R_model = modelo.evaluar_en_puntos(t_inicial, t_final, x0_cond, t_puntos)
        except Exception as e:
            # Si la simulación falla, devolver residuos grandes
            if verbose >= 2:
                print(f"⚠️  Simulación falló con parámetros {x}: {e}")
            return np.ones_like(T_obs) * 1e10
        
        # Residuos
        res = T_model - T_obs
        
        return res
    
    # Límites para los parámetros (todos deben ser >= 0)
    # beta debe estar en [0, 1] por ser una proporción
    bounds_lower = [0.0, 0.0, 0.0, 0.0]
    bounds_upper = [np.inf, np.inf, 1.0, np.inf]
    
    print(f"\nIniciando optimización...")
    print(f"Límites: θ≥0, ρ≥0, 0≤β≤1, γ≥0\n")
    
    # Optimización
    resultado = least_squares(
        residuos,
        x0,
        bounds=(bounds_lower, bounds_upper),
        method=metodo,
        verbose=verbose,
        max_nfev=1000,  # máximo de evaluaciones de función
        ftol=1e-8,
        xtol=1e-8,
        gtol=1e-8
    )
    
    # Extraer parámetros óptimos
    theta_opt, rho_opt, beta_opt, gamma_opt = resultado.x
    
    # Crear objeto con parámetros calibrados
    params_calibrados = ModeloParametros(
        **params_fijos,
        theta=theta_opt,
        rho=rho_opt,
        beta=beta_opt,
        gamma=gamma_opt
    )
    
    print("\n" + "="*60)
    print("RESULTADOS DE LA CALIBRACIÓN")
    print("="*60)
    print(f"\nÉxito: {resultado.success}")
    print(f"Mensaje: {resultado.message}")
    print(f"Número de evaluaciones: {resultado.nfev}")
    print(f"Costo final (suma de cuadrados de residuos): {resultado.cost:.6e}")
    
    print(f"\nParámetros calibrados:")
    print(f"  θ (theta) = {theta_opt:.6f} (inicial: {x0[0]:.6f})")
    print(f"  ρ (rho)   = {rho_opt:.6f} (inicial: {x0[1]:.6f})")
    print(f"  β (beta)  = {beta_opt:.6f} (inicial: {x0[2]:.6f})")
    print(f"  γ (gamma) = {gamma_opt:.6f} (inicial: {x0[3]:.6f})")
    
    # Calcular métricas con parámetros calibrados
    x0_cond = condiciones_iniciales(df, params_calibrados)
    modelo = ModeloSuicidio(params_calibrados, df['Poblacion_10ymas_P'], df['anio'])
    S_model, T_model, R_model = modelo.evaluar_en_puntos(t_inicial, t_final, x0_cond, t_puntos)
    
    metricas = calcular_metricas(T_obs, T_model)
    
    print(f"\nMétricas de ajuste:")
    print(f"  MAE (Error Absoluto Medio):     {metricas['MAE']:,.2f}")
    print(f"  RMSE (Raíz del Error Cuadrático): {metricas['RMSE']:,.2f}")
    print(f"  MAPE (Error Relativo Medio):    {metricas['MAPE']:.2f}%")
    print(f"  R² (Coef. Determinación):       {metricas['R2']:.4f}")
    print("="*60 + "\n")
    
    return params_calibrados, resultado


def calibrar_con_restricciones(
    df: pd.DataFrame,
    params_iniciales: ModeloParametros,
    theta_bounds: Optional[Tuple[float, float]] = None,
    rho_bounds: Optional[Tuple[float, float]] = None,
    beta_bounds: Optional[Tuple[float, float]] = None,
    gamma_bounds: Optional[Tuple[float, float]] = None,
    metodo: str = 'trf',
    verbose: int = 1
) -> Tuple[ModeloParametros, OptimizeResult]:
    """
    Calibra parámetros con restricciones personalizadas.
    
    Similar a calibrar_parametros pero permite especificar límites
    personalizados para cada parámetro.
    
    Args:
        df: DataFrame con los datos observados
        params_iniciales: Parámetros iniciales
        theta_bounds: Tupla (min, max) para theta (por defecto (0, inf))
        rho_bounds: Tupla (min, max) para rho (por defecto (0, inf))
        beta_bounds: Tupla (min, max) para beta (por defecto (0, 1))
        gamma_bounds: Tupla (min, max) para gamma (por defecto (0, inf))
        metodo: Método de optimización
        verbose: Nivel de verbosidad
    
    Returns:
        Tupla (params_calibrados, resultado_optimizacion)
    """
    # Límites por defecto
    if theta_bounds is None:
        theta_bounds = (0.0, np.inf)
    if rho_bounds is None:
        rho_bounds = (0.0, np.inf)
    if beta_bounds is None:
        beta_bounds = (0.0, 1.0)
    if gamma_bounds is None:
        gamma_bounds = (0.0, np.inf)
    
    # Guardar parámetros fijos
    params_fijos = {
        'delta': params_iniciales.delta,
        'delta_s': params_iniciales.delta_s,
        'delta_n': params_iniciales.delta_n,
        'm': params_iniciales.m,
        'phi': params_iniciales.phi,
        'psi': params_iniciales.psi,
    }
    
    # Valores iniciales
    x0 = np.array([
        params_iniciales.theta,
        params_iniciales.rho,
        params_iniciales.beta,
        params_iniciales.gamma
    ])
    
    # Datos observados
    T_obs = df['T_obs'].values
    t_puntos = df['anio'].values.astype(float)
    t_inicial = t_puntos[0]
    t_final = t_puntos[-1]
    
    # Función objetivo
    def residuos(x: np.ndarray) -> np.ndarray:
        theta, rho, beta, gamma = x
        
        params = ModeloParametros(
            **params_fijos,
            theta=theta,
            rho=rho,
            beta=beta,
            gamma=gamma
        )
        
        x0_cond = condiciones_iniciales(df, params)
        modelo = ModeloSuicidio(params, df['Poblacion_10ymas_P'], df['anio'])
        
        try:
            S_model, T_model, R_model = modelo.evaluar_en_puntos(t_inicial, t_final, x0_cond, t_puntos)
        except Exception:
            return np.ones_like(T_obs) * 1e10
        
        return T_model - T_obs
    
    # Límites personalizados
    bounds_lower = [theta_bounds[0], rho_bounds[0], beta_bounds[0], gamma_bounds[0]]
    bounds_upper = [theta_bounds[1], rho_bounds[1], beta_bounds[1], gamma_bounds[1]]
    
    # Optimización
    resultado = least_squares(
        residuos,
        x0,
        bounds=(bounds_lower, bounds_upper),
        method=metodo,
        verbose=verbose,
        max_nfev=1000
    )
    
    # Parámetros calibrados
    theta_opt, rho_opt, beta_opt, gamma_opt = resultado.x
    
    params_calibrados = ModeloParametros(
        **params_fijos,
        theta=theta_opt,
        rho=rho_opt,
        beta=beta_opt,
        gamma=gamma_opt
    )
    
    return params_calibrados, resultado
