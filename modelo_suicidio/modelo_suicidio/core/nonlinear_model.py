import numpy as np
from typing import Tuple, Callable
import pandas as pd
from scipy.integrate import solve_ivp
from .parameters import ModeloParametros

class ModeloNoLineal:
    def __init__(self, params: ModeloParametros, anios: np.ndarray, P: np.ndarray):
        """
        anios: vector de años (por ejemplo [2010, 2011, ..., 2024])
        P: vector de P(t) correspondiente (Poblacion_10ymas_P).
        Prepara un interpolador lineal P_t(t) sobre ese rango.
        """
        self.params = params
        self.anios = anios.astype(float)
        self.P = P.astype(float)
        
    def P_t(self, t: float) -> float:
        """
        Devuelve P(t) interpolando linealmente entre los valores anuales.
        """
        return np.interp(t, self.anios, self.P)

    def rhs(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Sistema no lineal:
        y = [S, T, R]
        Devuelve [dS/dt, dT/dt, dR/dt].
        """
        S, T, R = y
        
        # Parámetros
        delta_n = self.params.delta_n
        delta_s = self.params.delta_s
        theta = self.params.theta
        rho = self.params.rho
        beta = self.params.beta
        gamma = self.params.gamma
        
        P_val = self.P_t(t)
        
        # Evitar división por cero
        if P_val < 1e-9:
            P_val = 1.0

        # Términos explícitos según solicitud
        # Entrada a T por influencia social
        term_influencia = beta * delta_s * (T / P_val) * S
        
        # Entrada a T por otras causas
        term_otras = gamma * (1 - beta) * delta_s * S
        
        # Ecuaciones
        # dS/dt = theta * P(t) + (1 - delta_n) * R - term_otras - term_influencia - delta_s * S - delta_n * S
        dS = (theta * P_val) + ((1 - delta_n) * R) - term_otras - term_influencia - (delta_s * S) - (delta_n * S)
        
        # dT/dt = term_otras + term_influencia - rho * T - delta_s * T - delta_n * T
        dT = term_otras + term_influencia - (rho * T) - (delta_s * T) - (delta_n * T)
        
        # dR/dt = rho * T - R
        dR = (rho * T) - R
        
        return np.array([dS, dT, dR])

    def simular(self, t0: float, tf: float, x0: np.ndarray, num_puntos: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """
        Integra el sistema desde t0 hasta tf usando solve_ivp.
        x0 = [S0, T0, R0].
        Devuelve:
            t: vector de tiempos,
            X: matriz (num_puntos x 3) con columnas [S, T, R].
        """
        t_eval = np.linspace(t0, tf, num_puntos)
        
        sol = solve_ivp(
            fun=self.rhs,
            t_span=(t0, tf),
            y0=x0,
            t_eval=t_eval,
            method='RK45' # O LSODA si es rígido, pero RK45 suele ir bien
        )
        
        if not sol.success:
            print(f"Advertencia en simulación: {sol.message}")
            
        return sol.t, sol.y.T
