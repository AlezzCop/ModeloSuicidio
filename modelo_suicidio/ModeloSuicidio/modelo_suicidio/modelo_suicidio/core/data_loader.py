import pandas as pd

def cargar_datos_excel(ruta: str) -> pd.DataFrame:
    """
    Lee el archivo Excel (hoja 'Datos') y devuelve un DataFrame
    con columnas:
        anio,
        Poblacion_10ymas_P,
        defunciones_totales,
        defunciones_suicidio,
        T_obs,
    y, si faltan, calcula las tasas:
        delta_t  = defunciones_totales / P,
        delta_s_t = defunciones_suicidio / P,
        delta_n_t = delta_t - delta_s_t.
    """
    try:
        df = pd.read_excel(ruta, sheet_name='Datos')
    except Exception as e:
        raise ValueError(f"Error al leer el archivo Excel: {e}")

    required_cols = [
        'anio',
        'Poblacion_10ymas_P',
        'defunciones_totales',
        'defunciones_suicidio',
        'T_obs'
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # Calcular tasas si no existen
    if 'delta_t' not in df.columns:
        df['delta_t'] = df['defunciones_totales'] / df['Poblacion_10ymas_P']
    
    if 'delta_s_t' not in df.columns:
        df['delta_s_t'] = df['defunciones_suicidio'] / df['Poblacion_10ymas_P']
        
    if 'delta_n_t' not in df.columns:
        df['delta_n_t'] = df['delta_t'] - df['delta_s_t']

    return df
