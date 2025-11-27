import numpy as np
import pandas as pd
from .parameters import ModeloParametros
from .analysis import prueba_escritorio

def calculate_statistics(df: pd.DataFrame, params: ModeloParametros, anio_ini: int, anio_fin: int) -> dict:
    """
    Calcula estadísticos de ajuste (R2, MSE, RMSE, MAE, MAPE) comparando T_model vs T_obs.
    """
    # Ejecutar simulación para obtener datos comparados
    res_df = prueba_escritorio(df, params, anio_ini, anio_fin)
    
    # Filtrar filas válidas (donde hay T_obs)
    valid = res_df.dropna(subset=['T_obs', 'T_model'])
    
    if valid.empty:
        return {
            'R2': 0.0, 'MSE': 0.0, 'RMSE': 0.0, 'MAE': 0.0, 'MAPE': 0.0,
            'n_obs': 0
        }
    
    y_true = valid['T_obs'].values
    y_pred = valid['T_model'].values
    
    # R2
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    # MSE
    mse = np.mean((y_true - y_pred) ** 2)
    
    # RMSE
    rmse = np.sqrt(mse)
    
    # MAE
    mae = np.mean(np.abs(y_true - y_pred))
    
    # MAPE
    # Evitar división por cero
    mask_nonzero = y_true != 0
    if np.any(mask_nonzero):
        mape = np.mean(np.abs((y_true[mask_nonzero] - y_pred[mask_nonzero]) / y_true[mask_nonzero])) * 100
    else:
        mape = 0.0
        
    return {
        'R2': r2,
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape,
        'n_obs': len(y_true)
    }

def generate_conclusion_text(stats: dict, params: ModeloParametros) -> str:
    """
    Genera un texto explicativo basado en los estadísticos y parámetros.
    """
    r2 = stats.get('R2', 0)
    mape = stats.get('MAPE', 0)
    
    txt = "=== INFORME DE CONCLUSIONES DEL MODELO ===\n\n"
    
    # 1. Evaluación de Ajuste
    txt += "1. EVALUACIÓN DE AJUSTE\n"
    txt += f"El modelo tiene un R² de {r2:.4f}, "
    
    if r2 > 0.9:
        txt += "lo que indica un ajuste excelente a los datos observados.\n"
    elif r2 > 0.7:
        txt += "lo que indica un ajuste bueno a los datos observados.\n"
    elif r2 > 0.5:
        txt += "lo que indica un ajuste moderado a los datos observados.\n"
    else:
        txt += "lo que indica un ajuste pobre a los datos observados.\n"
        
    txt += f"El error porcentual medio (MAPE) es del {mape:.2f}%, "
    if mape < 10:
        txt += "lo que sugiere que las predicciones son muy precisas.\n\n"
    elif mape < 20:
        txt += "lo que sugiere algunas desviaciones en las predicciones.\n\n"
    else:
        txt += "lo que indica errores significativos en las predicciones.\n\n"
    
    # 2. Parámetros del Modelo
    txt += "2. PARÁMETROS DEL MODELO\n"
    txt += f"Los parámetros calibrados sugieren una tasa de iniciación (Beta) de {params.beta:.6f}, "
    if params.beta > 0.1: # Umbral arbitrario para "alto" vs "bajo" en este contexto
        txt += "lo que implica una propagación rápida del suicidio en la población vulnerable debido al contagio social.\n"
    else:
        txt += "lo que implica una propagación moderada o baja del suicidio en la población vulnerable.\n"
        
    txt += f"La tasa de transmisión externa (Gamma) es de {params.gamma:.6f}, lo que indica factores sociales importantes independientes del contagio.\n"
    
    txt += f"La tasa de recuperación (Rho) es de {params.rho:.6f}. "
    if params.rho > 0:
        tiempo_recup = 1/params.rho
        txt += f"Esto sugiere que el tiempo promedio en el estado de tratamiento es de aproximadamente {tiempo_recup:.2f} años.\n"
        if params.rho < 0.2: # < 0.2 significa > 5 años
             txt += "Si este valor es muy bajo, sugiere que el tiempo de tratamiento en el modelo es muy largo.\n"
    else:
        txt += "Esto sugiere que no hay recuperación significativa en el modelo.\n"
    txt += "\n"

    # 3. Conclusión General
    txt += "3. CONCLUSIÓN GENERAL\n"
    if r2 > 0.9 and mape < 10:
        txt += "El modelo sigue razonablemente los datos observados y captura bien la dinámica. Puede ser útil para planificación de políticas públicas."
    else:
        txt += "Aunque el modelo captura la tendencia general, existen desviaciones significativas (ajuste no ideal). "
        txt += "Se recomienda revisar los datos de entrada, las suposiciones sobre la dinámica del tratamiento y la recuperación, o recalibrar los parámetros para mejorar la precisión del modelo."
        
    return txt
