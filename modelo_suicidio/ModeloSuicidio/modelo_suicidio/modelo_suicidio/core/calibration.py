import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from .parameters import ModeloParametros
from .nonlinear_model import ModeloNoLineal
from .analysis import condiciones_iniciales

def calibrar_parametros(
    df: pd.DataFrame,
    params_base: ModeloParametros,
    anio_ini: int,
    anio_fin: int,
    num_theta: int = 5, # Mantenemos la firma pero usaremos la logica nueva
    num_gamma: int = 5,
    progress_callback = None
) -> tuple[ModeloParametros, float, str]:
    """
    Busca valores de theta, rho, beta y gamma que minimicen la diferencia
    entre T_model y T_obs en [anio_ini, anio_fin].
    
    Usa un punto inicial robusto y límites definidos por el usuario.
    """
    
    anios_data = df['anio'].values
    P_data = df['Poblacion_10ymas_P'].values
    
    # Datos observados para comparar (años enteros)
    mask = (df['anio'] >= anio_ini) & (df['anio'] <= anio_fin)
    df_subset = df.loc[mask]
    t_obs_vals = df_subset['anio'].values
    T_obs_vals = df_subset['T_obs'].values
    
    # Punto inicial sugerido
    # theta0 ~ delta_n (aprox 0.007), rho0=0.1, beta0=0.3, gamma0=10.0
    x0 = [params_base.delta_n, 0.1, 0.3, 10.0]
    
    # Límites: theta, rho, beta en [0, 1], gamma en [0, 20]
    bounds = (
        [0.0, 0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0, 20.0]
    )
    
    log_str = "Iniciando calibración con parámetros iniciales:\n"
    log_str += f"Theta: {x0[0]}, Rho: {x0[1]}, Beta: {x0[2]}, Gamma: {x0[3]}\n"
    
    def residuals(p_vec):
        theta, rho, beta, gamma = p_vec
        
        # Actualizar params
        p = ModeloParametros(
            delta=params_base.delta,
            delta_s=params_base.delta_s,
            delta_n=params_base.delta_n,
            m=params_base.m,
            phi=params_base.phi,
            psi=params_base.psi,
            theta=theta,
            rho=rho,
            beta=beta,
            gamma=gamma
        )
        
        modelo = ModeloNoLineal(p, anios_data, P_data)
        
        # Condiciones iniciales
        try:
            init_cond = condiciones_iniciales(df, p, anio_ini)
        except Exception:
            return np.full_like(T_obs_vals, 1e6)
            
        # Simular
        # Importante: simular en el rango continuo y luego interpolar, 
        # o usar t_eval en solve_ivp. Usaremos t_eval para exactitud en los puntos.
        try:
            from scipy.integrate import solve_ivp
            sol = solve_ivp(
                fun=modelo.rhs,
                t_span=(anio_ini, anio_fin),
                y0=init_cond,
                t_eval=t_obs_vals, # Evaluar exactamente en los años observados
                method='RK45'
            )
            
            if sol.status != 0 or not sol.success:
                return np.full_like(T_obs_vals, 1e6)
                
            T_model = sol.y[1] # La segunda fila es T
            
            # Verificar longitudes
            if len(T_model) != len(T_obs_vals):
                return np.full_like(T_obs_vals, 1e6)
                
            # Retornar residuos (T_model - T_obs)
            return T_model - T_obs_vals
            
        except Exception as e:
            return np.full_like(T_obs_vals, 1e6)

    # Ejecutar optimización
    res = least_squares(residuals, x0, bounds=bounds, method='trf', verbose=0)
    
    best_params_vec = res.x
    best_cost = res.cost
    
    # Traducir mensaje de resultado
    msg_traducido = res.message
    if "`ftol` termination condition is satisfied" in res.message:
        msg_traducido = "Convergencia alcanzada (criterio de tolerancia ftol satisfecho)."
    elif "`gtol` termination condition is satisfied" in res.message:
        msg_traducido = "Convergencia alcanzada (criterio de gradiente gtol satisfecho)."
    elif "`xtol` termination condition is satisfied" in res.message:
        msg_traducido = "Convergencia alcanzada (criterio de paso xtol satisfecho)."
    elif "The maximum number of function evaluations is exceeded" in res.message:
        msg_traducido = "Se excedió el número máximo de evaluaciones."
    
    log_str += f"\nCalibración finalizada.\nCosto final (suma cuadrados residuos / 2): {best_cost:.4f}\n"
    log_str += f"Éxito: {res.success}\nMensaje: {msg_traducido}\n"
    
    final_params = ModeloParametros(
        delta=params_base.delta,
        delta_s=params_base.delta_s,
        delta_n=params_base.delta_n,
        m=params_base.m,
        phi=params_base.phi,
        psi=params_base.psi,
        theta=best_params_vec[0],
        rho=best_params_vec[1],
        beta=best_params_vec[2],
        gamma=best_params_vec[3]
    )
    
    return final_params, best_cost, log_str
