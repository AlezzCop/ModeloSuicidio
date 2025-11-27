"""
Módulo que implementa el sistema de ecuaciones diferenciales ordinarias (EDO)
del modelo no lineal de dinámica poblacional del suicidio.

Implementa la ecuación (9) del artículo Granada et al. (2023):
    dS/dt = θP(t) + (1-δₙ)R - γ(1-β)δₛS - βδₛ(T/P)S - δₛS - δₙS
    dT/dt = γ(1-β)δₛS + βδₛ(T/P)S - ρT - δₛT - δₙT
    dR/dt = ρT - R
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from typing import Tuple
from .parameters import ModeloParametros


class ModeloSuicidio:
    """
    Clase que encapsula el modelo de dinámica poblacional del suicidio.
    
    El modelo tiene tres compartimentos:
        S(t): Población susceptible
        T(t): Población en tratamiento
        R(t): Población recuperada
    
    Y una serie exógena:
        P(t): Población vulnerable total (≥ 10 años)
    """
    
    def __init__(self, parametros: ModeloParametros, series_P: pd.Series, series_anio: pd.Series):
        """
        Inicializa el modelo con los parámetros y la serie temporal de P(t).
        
        Args:
            parametros: Objeto ModeloParametros con todos los parámetros
            series_P: Serie de Pandas con los valores de P por año
            series_anio: Serie de Pandas con los años correspondientes
        """
        self.param = parametros
        self.series_P = series_P.values
        self.series_anio = series_anio.values
        
        # Verificar que P y años tengan la misma longitud
        if len(self.series_P) != len(self.series_anio):
            raise ValueError("series_P y series_anio deben tener la misma longitud")
        
        # Ordenar por año (por si acaso)
        indices_ordenados = np.argsort(self.series_anio)
        self.series_anio = self.series_anio[indices_ordenados]
        self.series_P = self.series_P[indices_ordenados]
    
    def P_t(self, t: float) -> float:
        """
        Devuelve P(t) interpolando linealmente a partir de los datos anuales.
        
        t se trata como año en escala continua (por ejemplo 2010.0, 2010.5, etc.).
        Si t está fuera del rango de datos, se extrapola linealmente.
        
        Args:
            t: Tiempo (año) para el cual calcular P
        
        Returns:
            Valor de P(t) interpolado
        """
        # Interpolación lineal
        P = np.interp(t, self.series_anio, self.series_P)
        return P
    
    def rhs(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Calcula las derivadas del sistema de EDO.
        
        Sistema de ecuaciones (9) del artículo:
            dS/dt = θP(t) + (1-δₙ)R - γ(1-β)δₛS - βδₛ(T/P)S - δₛS - δₙS
            dT/dt = γ(1-β)δₛS + βδₛ(T/P)S - ρT - δₛT - δₙT
            dR/dt = ρT - R
        
        Args:
            t: Tiempo actual (año)
            y: Vector de estado [S, T, R]
        
        Returns:
            Vector de derivadas [dS/dt, dT/dt, dR/dt]
        """
        S, T, R = y
        
        # Obtener P(t) interpolado
        P = self.P_t(t)
        
        # Evitar divisiones por cero
        if P < 1.0:
            P = 1.0
        
        # Parámetros (notación del artículo)
        theta = self.param.theta
        rho = self.param.rho
        beta = self.param.beta
        gamma = self.param.gamma
        delta_s = self.param.delta_s
        delta_n = self.param.delta_n
        
        # Términos auxiliares para claridad
        # Entrada a S desde P
        entrada_S_desde_P = theta * P
        
        # Regreso de R a S (recuperados que recaen)
        regreso_R_a_S = (1 - delta_n) * R
        
        # Salida de S por influencia propia (sin contagio)
        salida_S_influencia = gamma * (1 - beta) * delta_s * S
        
        # Salida de S por contagio (proporcional a T/P)
        salida_S_contagio = beta * delta_s * (T / P) * S
        
        # Mortalidad de S
        mortalidad_S_suicidio = delta_s * S
        mortalidad_S_natural = delta_n * S
        
        # Ecuación para dS/dt
        dS_dt = (entrada_S_desde_P + regreso_R_a_S 
                 - salida_S_influencia - salida_S_contagio 
                 - mortalidad_S_suicidio - mortalidad_S_natural)
        
        # Entrada a T desde S (influencia + contagio)
        entrada_T_desde_S = salida_S_influencia + salida_S_contagio
        
        # Salida de T por recuperación
        salida_T_recuperacion = rho * T
        
        # Mortalidad de T
        mortalidad_T_suicidio = delta_s * T
        mortalidad_T_natural = delta_n * T
        
        # Ecuación para dT/dt
        dT_dt = (entrada_T_desde_S - salida_T_recuperacion 
                 - mortalidad_T_suicidio - mortalidad_T_natural)
        
        # Entrada a R desde T
        entrada_R_desde_T = salida_T_recuperacion
        
        # Salida de R (regreso a S + mortalidad natural implícita en regreso_R_a_S)
        salida_R = R
        
        # Ecuación para dR/dt
        dR_dt = entrada_R_desde_T - salida_R
        
        return np.array([dS_dt, dT_dt, dR_dt])
    
    def simular(
        self,
        t_inicial: float,
        t_final: float,
        x0: np.ndarray,
        num_pasos: int = 200,
        metodo: str = 'RK45'
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Integra el sistema de EDO desde t_inicial hasta t_final.
        
        Args:
            t_inicial: Tiempo inicial (año)
            t_final: Tiempo final (año)
            x0: Condiciones iniciales [S0, T0, R0]
            num_pasos: Número de puntos de evaluación (por defecto 200)
            metodo: Método de integración para solve_ivp (por defecto 'RK45')
        
        Returns:
            Tupla (t, S, T, R) con arrays de numpy:
                t: Vector de tiempos
                S: Vector de valores de S(t)
                T: Vector de valores de T(t)
                R: Vector de valores de R(t)
        """
        # Puntos donde evaluar la solución
        t_eval = np.linspace(t_inicial, t_final, num_pasos)
        
        # Resolver el sistema de EDO
        sol = solve_ivp(
            fun=self.rhs,
            t_span=(t_inicial, t_final),
            y0=x0,
            method=metodo,
            t_eval=t_eval,
            dense_output=True,
            vectorized=False
        )
        
        if not sol.success:
            raise RuntimeError(f"La integración falló: {sol.message}")
        
        # Extraer resultados
        t = sol.t
        S = sol.y[0]
        T = sol.y[1]
        R = sol.y[2]
        
        return t, S, T, R
    
    def evaluar_en_puntos(
        self,
        t_inicial: float,
        t_final: float,
        x0: np.ndarray,
        t_puntos: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Integra el sistema y evalúa en puntos específicos de tiempo.
        
        Útil para comparar con datos observados en años discretos.
        
        Args:
            t_inicial: Tiempo inicial (año)
            t_final: Tiempo final (año)
            x0: Condiciones iniciales [S0, T0, R0]
            t_puntos: Array con los tiempos donde evaluar
        
        Returns:
            Tupla (S, T, R) evaluadas en t_puntos
        """
        # Resolver con dense_output para poder evaluar en cualquier punto
        sol = solve_ivp(
            fun=self.rhs,
            t_span=(t_inicial, t_final),
            y0=x0,
            method='RK45',
            dense_output=True,
            vectorized=False
        )
        
        if not sol.success:
            raise RuntimeError(f"La integración falló: {sol.message}")
        
        # Evaluar en los puntos solicitados
        S_puntos = sol.sol(t_puntos)[0]
        T_puntos = sol.sol(t_puntos)[1]
        R_puntos = sol.sol(t_puntos)[2]
        
        return S_puntos, T_puntos, R_puntos
