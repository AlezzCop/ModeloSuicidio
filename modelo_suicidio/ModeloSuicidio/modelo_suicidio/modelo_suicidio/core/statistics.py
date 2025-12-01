import numpy as np
import pandas as pd
from .parameters import ModeloParametros
from .analysis import prueba_escritorio

def calculate_statistics(df: pd.DataFrame, params: ModeloParametros, anio_ini: int, anio_fin: int) -> dict:
    """
    Calcula estadísticos de ajuste (R2, MSE, RMSE, MAE, MAPE) comparando T_model vs T_obs.
    Retorna un diccionario con las métricas y el DataFrame de resultados simulados.
    """
    # Ejecutar simulación para obtener datos comparados
    res_df = prueba_escritorio(df, params, anio_ini, anio_fin)
    
    # Filtrar filas válidas (donde hay T_obs)
    valid = res_df.dropna(subset=['T_obs', 'T_model'])
    
    if valid.empty:
        return {
            'R2': 0.0, 'MSE': 0.0, 'RMSE': 0.0, 'MAE': 0.0, 'MAPE': 0.0,
            'n_obs': 0, 'res_df': res_df
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
        'n_obs': len(y_true),
        'res_df': res_df
    }

def generar_texto_conclusion_detallada(
    stats: dict,
    params: ModeloParametros,
    df_resultados: pd.DataFrame,
    anio_ini: int,
    anio_fin: int
) -> str:
    """
    Construye el texto de conclusiones siguiendo la estructura descrita:
    resumen general, comparación datos vs modelo, interpretación de métricas,
    interpretación de parámetros y conclusión general.
    Usa lenguaje claro en español y condicionales basados en R² y MAPE
    para clasificar la calidad del ajuste.
    """
    r2 = stats.get('R2', 0)
    mape = stats.get('MAPE', 0)
    rmse = stats.get('RMSE', 0)
    mae = stats.get('MAE', 0)
    
    # Filtrar datos válidos para análisis detallado
    valid = df_resultados.dropna(subset=['T_obs', 'T_model']).copy()
    if valid.empty:
        return "No hay suficientes datos observados para generar conclusiones detalladas."
        
    t_obs_mean = valid['T_obs'].mean()
    t_model_mean = valid['T_model'].mean()
    diff_mean = t_model_mean - t_obs_mean
    
    # Calcular errores por año
    valid['error'] = valid['T_model'] - valid['T_obs']
    valid['error_rel'] = (valid['error'] / valid['T_obs']).abs() * 100
    
    idx_max_error = valid['error_rel'].idxmax()
    anio_max_error = valid.loc[idx_max_error, 'anio']
    max_error_rel = valid.loc[idx_max_error, 'error_rel']
    error_max_abs = valid.loc[idx_max_error, 'error']
    
    txt = "=== INFORME DE CONCLUSIONES DEL MODELO ===\n\n"
    
    # 1. RESUMEN GENERAL
    txt += "1. RESUMEN GENERAL\n"
    calidad = ""
    if r2 >= 0.9 and mape < 10:
        calidad = "Muy bueno"
        desc = "El modelo logra seguir con gran precisión la tendencia de los casos en tratamiento."
    elif r2 >= 0.7 and mape < 20:
        calidad = "Bueno/Aceptable"
        desc = "El modelo logra seguir bastante bien la tendencia de los casos en tratamiento, aunque presenta errores moderados en algunos años."
    else:
        calidad = "Débil"
        desc = "El modelo tiene dificultades para capturar la variabilidad de los datos observados, presentando desviaciones importantes."
        
    txt += f"El ajuste del modelo se considera: {calidad}.\n"
    txt += f"{desc}\n\n"
    
    # 2. COMPARACIÓN DATOS OBSERVADOS VS SIMULADOS
    txt += "2. COMPARACIÓN ENTRE DATOS OBSERVADOS Y SIMULADOS\n"
    txt += f"En el periodo analizado ({anio_ini}-{anio_fin}):\n"
    txt += f"- Promedio de casos observados: {t_obs_mean:.1f}\n"
    txt += f"- Promedio de casos simulados: {t_model_mean:.1f}\n"
    
    if diff_mean > 0:
        txt += f"En promedio, el modelo sobreestima los casos en tratamiento en alrededor de {abs(diff_mean):.0f} personas por año.\n"
    else:
        txt += f"En promedio, el modelo subestima los casos en tratamiento en alrededor de {abs(diff_mean):.0f} personas por año.\n"
        
    txt += f"El mayor error relativo se observa en {int(anio_max_error)}, donde el modelo "
    if error_max_abs > 0:
        txt += f"sobreestima en aproximadamente {error_max_abs:.0f} casos ({max_error_rel:.1f}%).\n\n"
    else:
        txt += f"subestima en aproximadamente {abs(error_max_abs):.0f} casos ({max_error_rel:.1f}%).\n\n"

    # 3. INTERPRETACIÓN DE LAS MÉTRICAS
    txt += "3. INTERPRETACIÓN DE LAS MÉTRICAS\n"
    txt += f"- R² ({r2:.4f}): Indica que el modelo explica el {r2*100:.1f}% de la variabilidad de los datos observados.\n"
    txt += f"- RMSE ({rmse:.1f}) / MAE ({mae:.1f}): En promedio, las predicciones del modelo se alejan {mae:.1f} casos de los valores reales.\n"
    txt += f"- MAPE ({mape:.2f}%): Significa que, en promedio, las predicciones del modelo se desvían un {mape:.2f}% de los datos observados.\n\n"
    
    # 4. PARÁMETROS DEL MODELO
    txt += "4. PARÁMETROS DEL MODELO\n"
    txt += f"- Beta (β = {params.beta:.6f}): Intensidad del 'contagio' o influencia social.\n"
    if params.beta > 0.1:
        txt += "  Un valor alto sugiere que la influencia social juega un papel crucial en la propagación.\n"
    else:
        txt += "  Un valor bajo sugiere que la influencia social tiene un efecto moderado o limitado.\n"
        
    txt += f"- Gamma (γ = {params.gamma:.6f}): Fuerza de factores externos que llevan a tratamiento.\n"
    txt += "  Representa la entrada a tratamiento por causas ajenas al contagio social (factores económicos, personales, etc.).\n"
    
    txt += f"- Rho (ρ = {params.rho:.6f}): Velocidad de salida de tratamiento (recuperación).\n"
    if params.rho > 0:
        tiempo_recup = 1/params.rho
        txt += f"  Este valor sugiere un tiempo promedio de permanencia en tratamiento de aproximadamente {tiempo_recup:.2f} años.\n"
    else:
        txt += "  El valor es 0, lo que implica que no hay salida de tratamiento en el modelo.\n"
        
    txt += f"- Theta (θ = {params.theta:.6f}): Entrada desde población vulnerable a susceptibles.\n\n"
    
    # 5. COMENTARIO SOBRE LA TABLA COMPARATIVA
    txt += "5. COMENTARIO SOBRE LA TABLA COMPARATIVA\n"
    txt += generar_conclusion_tabla_comparativa(df_resultados) + "\n\n"

    # 6. CONCLUSIÓN GENERAL
    txt += "6. CONCLUSIÓN GENERAL\n"
    if calidad == "Muy bueno":
        txt += "El modelo es muy útil para describir la dinámica de T(t) en Oaxaca y puede usarse con confianza para proyecciones a corto plazo."
    elif calidad == "Bueno/Aceptable":
        txt += "El modelo es útil para entender la tendencia general, pero se debe tener precaución con las predicciones exactas en años específicos."
        txt += " Se recomienda revisar si hay eventos externos en los años de mayor error que no están siendo capturados."
    else:
        txt += "El modelo actual no captura adecuadamente la dinámica observada. Se recomienda:\n"
        txt += " - Revisar la calidad de los datos observados.\n"
        txt += " - Intentar calibrar con un rango de años diferente.\n"
        txt += " - Considerar si los supuestos del modelo (ej. parámetros constantes) son válidos para todo el periodo."
        
    return txt

def generar_conclusion_tabla_comparativa(df_resultados: pd.DataFrame) -> str:
    """
    A partir de la tabla comparativa (anio, T_obs, T_model, error_abs, error_rel),
    genera un breve texto en español que:
      - Mencione si en promedio el modelo tiende a sobreestimar o subestimar T_obs.
      - Indique el año con mayor error relativo y el valor aproximado del error.
      - Comente si los errores tienden a ser mayores al inicio, en la mitad o al final del periodo.
    """
    valid = df_resultados.dropna(subset=['T_obs', 'T_model']).copy()
    if valid.empty:
        return "No hay datos suficientes para analizar la tabla comparativa."

    # Asegurar columnas de error
    if 'error' not in valid.columns:
        valid['error'] = valid['T_model'] - valid['T_obs']
    if 'error_rel' not in valid.columns:
        valid['error_rel'] = (valid['error'] / valid['T_obs']).abs() * 100

    # 1. Sobre/Subestimación promedio
    mean_error = valid['error'].mean()
    if mean_error > 0:
        tendencia = "tiende a sobreestimar ligeramente"
    else:
        tendencia = "tiende a subestimar ligeramente"
    
    txt = f"Al observar la tabla comparativa, se nota que el modelo {tendencia} los valores observados (error medio de {mean_error:.1f} casos). "

    # 2. Año con mayor error
    idx_max = valid['error_rel'].idxmax()
    anio_max = valid.loc[idx_max, 'anio']
    err_max = valid.loc[idx_max, 'error_rel']
    txt += f"La mayor discrepancia relativa ocurre en el año {int(anio_max)} con un error del {err_max:.1f}%. "

    # 3. Distribución temporal del error (Inicio vs Final)
    # Dividir en dos mitades
    mid_idx = len(valid) // 2
    first_half = valid.iloc[:mid_idx]
    second_half = valid.iloc[mid_idx:]

    mean_err_rel_1 = first_half['error_rel'].mean() if not first_half.empty else 0
    mean_err_rel_2 = second_half['error_rel'].mean() if not second_half.empty else 0

    if abs(mean_err_rel_1 - mean_err_rel_2) < 2.0:
        txt += "Los errores se mantienen relativamente constantes a lo largo del periodo."
    elif mean_err_rel_1 > mean_err_rel_2:
        txt += "Los errores tienden a ser mayores al inicio del periodo, mejorando el ajuste en los años más recientes."
    else:
        txt += "El ajuste es mejor al inicio, pero los errores aumentan en los años finales del periodo."

    return txt

# Mantener compatibilidad hacia atrás si es necesario, o eliminar si ya no se usa
def generate_conclusion_text(stats: dict, params: ModeloParametros) -> str:
    """
    DEPRECATED: Use generar_texto_conclusion_detallada instead.
    Wrapper para mantener compatibilidad si algo más lo llama.
    """
    # Necesitamos un DF dummy o el real si estuviera en stats.
    # Si stats tiene 'res_df', lo usamos.
    if 'res_df' in stats:
        res_df = stats['res_df']
        # Inferir anios
        anio_ini = int(res_df['anio'].min())
        anio_fin = int(res_df['anio'].max())
        return generar_texto_conclusion_detallada(stats, params, res_df, anio_ini, anio_fin)
    else:
        return "Error: No se puede generar el texto detallado sin el DataFrame de resultados."
