"""
Módulo para definición y estimación de parámetros del modelo.

Define la clase ModeloParametros con todos los parámetros del sistema
y funciones para estimar sus valores a partir de los datos observados.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ModeloParametros:
    """
    Clase de datos para los parámetros del modelo de dinámica del suicidio.
    
    Parámetros básicos (estimados de los datos):
        delta (δ): Tasa media de defunción total
        delta_s (δ_s): Tasa media de defunción por suicidio
        delta_n (δ_n): Tasa media de defunción por otras causas (δ_n = δ - δ_s)
        m: Tasa global de tratamiento (media geométrica de T/P)
        phi (φ): Proporción de T que pasa a R
        psi (ψ): Proporción de P que está en S (relación: ψ = 1 - m - φm)
    
    Parámetros a calibrar:
        theta (θ): Tasa de paso de vulnerable a susceptible
        rho (ρ): Tasa de salida de T hacia R (recuperación)
        beta (β): Proporción de entrada a T por influencia/contagio
        gamma (γ): Factor de proporción para entrada a T por otras causas
    """
    delta: float      # δ: tasa media de defunción total
    delta_s: float    # δ_s: tasa media de defunción por suicidio
    delta_n: float    # δ_n: tasa media de defunción por otras causas
    m: float          # m: tasa global de tratamiento
    phi: float        # φ: proporción de T que pasa a R
    psi: float        # ψ: proporción de P que está en S
    theta: float      # θ: tasa de paso de vulnerable a susceptible
    rho: float        # ρ: tasa de recuperación
    beta: float       # β: proporción por influencia
    gamma: float      # γ: factor de otras causas
    
    def __str__(self) -> str:
        """Representación en string de los parámetros."""
        return (
            f"Parámetros del Modelo:\n"
            f"  Parámetros básicos (estimados):\n"
            f"    δ (delta):     {self.delta:.6f}\n"
            f"    δ_s (delta_s): {self.delta_s:.6f}\n"
            f"    δ_n (delta_n): {self.delta_n:.6f}\n"
            f"    m:             {self.m:.6f}\n"
            f"    φ (phi):       {self.phi:.6f}\n"
            f"    ψ (psi):       {self.psi:.6f}\n"
            f"  Parámetros del modelo (a calibrar):\n"
            f"    θ (theta):     {self.theta:.6f}\n"
            f"    ρ (rho):       {self.rho:.6f}\n"
            f"    β (beta):      {self.beta:.6f}\n"
            f"    γ (gamma):     {self.gamma:.6f}"
        )


def estimar_tasas_defuncion(df: pd.DataFrame) -> Tuple[float, float, float]:
    """
    Estima las tasas de defunción a partir de los datos observados.
    
    Calcula para cada año i:
        δ_i = defunciones_totales_i / P_i
        δ_s_i = defunciones_suicidio_i / P_i
        δ_n_i = δ_i - δ_s_i
    
    Y devuelve los promedios sobre todos los años.
    
    Args:
        df: DataFrame con columnas 'defunciones_totales', 'defunciones_suicidio', 'Poblacion_10ymas_P'
    
    Returns:
        Tupla (delta, delta_s, delta_n) con las tasas promedio
    """
    # Calcular tasas por año
    delta_i = df['defunciones_totales'] / df['Poblacion_10ymas_P']
    delta_s_i = df['defunciones_suicidio'] / df['Poblacion_10ymas_P']
    delta_n_i = delta_i - delta_s_i
    
    # Promediar
    delta = delta_i.mean()
    delta_s = delta_s_i.mean()
    delta_n = delta_n_i.mean()
    
    # Validar coherencia
    assert abs(delta - (delta_s + delta_n)) < 1e-10, "Error: δ ≠ δ_s + δ_n"
    
    return delta, delta_s, delta_n


def estimar_m(df: pd.DataFrame) -> float:
    """
    Calcula la tasa global de tratamiento m como media geométrica.
    
    Para cada año i calcula:
        m_i = T_obs_i / P_i
    
    Y devuelve la media geométrica:
        m = exp(promedio(ln(m_i)))
    
    Ignora años con T_obs <= 0.
    
    Args:
        df: DataFrame con columnas 'T_obs' y 'Poblacion_10ymas_P'
    
    Returns:
        Tasa global de tratamiento m (media geométrica)
    """
    # Calcular m_i para cada año
    m_i = df['T_obs'] / df['Poblacion_10ymas_P']
    
    # Filtrar valores válidos (> 0)
    m_i_validos = m_i[m_i > 0]
    
    if len(m_i_validos) == 0:
        raise ValueError("No hay valores válidos de T_obs para calcular m")
    
    # Media geométrica: exp(promedio(ln(m_i)))
    m = np.exp(np.mean(np.log(m_i_validos)))
    
    return m


def estimar_phi_psi(m: float, phi: float = 0.5) -> Tuple[float, float]:
    """
    Calcula psi a partir de m y phi usando la relación del artículo.
    
    La relación entre los parámetros es:
        ψ = 1 - m - φ·m
    
    Esta ecuación viene de la conservación: S + T + R = P en estado estacionario,
    donde T = m·P y R = φ·T = φ·m·P, por lo tanto S = P - T - R = P(1 - m - φ·m) = ψ·P
    
    Args:
        m: Tasa global de tratamiento
        phi: Proporción de T que pasa a R (por defecto 0.5)
    
    Returns:
        Tupla (phi, psi)
    
    Raises:
        ValueError: Si la relación resulta en ψ < 0
    """
    psi = 1.0 - m - phi * m
    
    if psi < 0:
        raise ValueError(
            f"Parámetros inconsistentes: ψ = 1 - m - φ·m = {psi:.6f} < 0\n"
            f"Con m = {m:.6f} y φ = {phi:.6f}\n"
            f"Pruebe reducir φ o verificar los datos."
        )
    
    return phi, psi


def parametros_iniciales(
    df: pd.DataFrame,
    phi: float = 0.5,
    theta: float = 0.01,
    rho: float = 0.1,
    beta: float = 0.3,
    gamma: float = 0.7
) -> ModeloParametros:
    """
    Calcula un objeto ModeloParametros con valores iniciales.
    
    Estima los parámetros básicos (delta, delta_s, delta_n, m, phi, psi) a partir
    de los datos y usa valores iniciales razonables para los parámetros a calibrar
    (theta, rho, beta, gamma).
    
    Args:
        df: DataFrame con los datos observados
        phi: Proporción de T que pasa a R (por defecto 0.5)
        theta: Tasa de paso de vulnerable a susceptible (por defecto 0.01)
        rho: Tasa de recuperación (por defecto 0.1)
        beta: Proporción por influencia (por defecto 0.3)
        gamma: Factor de otras causas (por defecto 0.7)
    
    Returns:
        Objeto ModeloParametros con todos los parámetros
    """
    # Estimar parámetros básicos
    delta, delta_s, delta_n = estimar_tasas_defuncion(df)
    m = estimar_m(df)
    phi, psi = estimar_phi_psi(m, phi)
    
    # Crear objeto con todos los parámetros
    params = ModeloParametros(
        delta=delta,
        delta_s=delta_s,
        delta_n=delta_n,
        m=m,
        phi=phi,
        psi=psi,
        theta=theta,
        rho=rho,
        beta=beta,
        gamma=gamma
    )
    
    return params


def validar_parametros(params: ModeloParametros) -> bool:
    """
    Valida que los parámetros estén en rangos físicamente razonables.
    
    Args:
        params: Objeto ModeloParametros a validar
    
    Returns:
        True si los parámetros son válidos
    
    Raises:
        ValueError: Si algún parámetro está fuera de rango
    """
    # Validar que tasas sean no negativas
    if params.delta < 0:
        raise ValueError(f"delta debe ser >= 0, recibido: {params.delta}")
    if params.delta_s < 0:
        raise ValueError(f"delta_s debe ser >= 0, recibido: {params.delta_s}")
    if params.delta_n < 0:
        raise ValueError(f"delta_n debe ser >= 0, recibido: {params.delta_n}")
    
    # Validar coherencia de deltas
    if abs(params.delta - (params.delta_s + params.delta_n)) > 1e-6:
        raise ValueError(f"delta debe ser igual a delta_s + delta_n")
    
    # Validar proporciones (0 <= proporción <= 1)
    if not (0 <= params.phi <= 1):
        raise ValueError(f"phi debe estar en [0, 1], recibido: {params.phi}")
    if not (0 <= params.psi <= 1):
        raise ValueError(f"psi debe estar en [0, 1], recibido: {params.psi}")
    if not (0 <= params.beta <= 1):
        raise ValueError(f"beta debe estar en [0, 1], recibido: {params.beta}")
    
    # Validar m (tasa de tratamiento debe ser razonable)
    if params.m < 0:
        raise ValueError(f"m debe ser >= 0, recibido: {params.m}")
    if params.m > 0.5:
        print(f"⚠️  Advertencia: m = {params.m:.4f} parece alto (>50% de P en tratamiento)")
    
    # Validar theta y rho (tasas de transición)
    if params.theta < 0:
        raise ValueError(f"theta debe ser >= 0, recibido: {params.theta}")
    if params.rho < 0:
        raise ValueError(f"rho debe ser >= 0, recibido: {params.rho}")
    
    # Validar gamma
    if params.gamma < 0:
        raise ValueError(f"gamma debe ser >= 0, recibido: {params.gamma}")
    
    return True
