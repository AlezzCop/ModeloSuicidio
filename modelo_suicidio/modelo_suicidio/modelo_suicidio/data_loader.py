"""
Módulo para carga y procesamiento de datos desde archivos Excel.

Este módulo provee funciones para leer datos de población, defunciones y
casos en tratamiento desde archivos Excel, validando el formato esperado.
"""

import pandas as pd
from typing import Optional


def cargar_datos_excel(ruta_excel: str, hoja: Optional[str] = None) -> pd.DataFrame:
    """
    Lee el archivo Excel con los datos de población y defunciones.
    
    El archivo debe contener las siguientes columnas:
        - anio: Año de la observación (int)
        - Poblacion_10ymas_P: Población vulnerable ≥ 10 años (float)
        - defunciones_totales: Total de defunciones ese año (int)
        - defunciones_suicidio: Defunciones por suicidio ese año (int)
        - T_obs: Población en tratamiento observada (float)
    
    Args:
        ruta_excel: Ruta al archivo Excel
        hoja: Nombre de la hoja a leer (opcional, usa la primera hoja por defecto)
    
    Returns:
        DataFrame con los datos limpios y tipos correctos
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si faltan columnas requeridas o hay datos inválidos
    """
    try:
        # Leer el archivo Excel
        if hoja:
            df = pd.read_excel(ruta_excel, sheet_name=hoja)
        else:
            df = pd.read_excel(ruta_excel)
        
        # Columnas requeridas
        columnas_requeridas = [
            'anio',
            'Poblacion_10ymas_P',
            'defunciones_totales',
            'defunciones_suicidio',
            'T_obs'
        ]
        
        # Verificar que todas las columnas requeridas estén presentes
        columnas_faltantes = set(columnas_requeridas) - set(df.columns)
        if columnas_faltantes:
            raise ValueError(
                f"Faltan las siguientes columnas en el Excel: {', '.join(columnas_faltantes)}\n"
                f"Columnas encontradas: {', '.join(df.columns)}"
            )
        
        # Convertir tipos de datos
        df['anio'] = df['anio'].astype(int)
        
        # Limpiar espacios en columnas numéricas (formato europeo con separadores de miles)
        # Eliminar espacios antes de convertir a float/int
        df['Poblacion_10ymas_P'] = df['Poblacion_10ymas_P'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)
        df['defunciones_totales'] = df['defunciones_totales'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(int)
        df['defunciones_suicidio'] = df['defunciones_suicidio'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(int)
        df['T_obs'] = df['T_obs'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)
        
        # Ordenar por año
        df = df.sort_values('anio').reset_index(drop=True)
        
        # Validar que no haya valores negativos
        if (df['Poblacion_10ymas_P'] < 0).any():
            raise ValueError("Hay valores negativos en Poblacion_10ymas_P")
        if (df['defunciones_totales'] < 0).any():
            raise ValueError("Hay valores negativos en defunciones_totales")
        if (df['defunciones_suicidio'] < 0).any():
            raise ValueError("Hay valores negativos en defunciones_suicidio")
        if (df['T_obs'] < 0).any():
            raise ValueError("Hay valores negativos en T_obs")
        
        # Validar coherencia de datos
        if (df['defunciones_suicidio'] > df['defunciones_totales']).any():
            raise ValueError("Hay años donde defunciones_suicidio > defunciones_totales")
        
        # Calcular tasas auxiliares (opcional, para verificación)
        df['delta_t'] = df['defunciones_totales'] / df['Poblacion_10ymas_P']
        df['delta_s_t'] = df['defunciones_suicidio'] / df['Poblacion_10ymas_P']
        df['delta_n_t'] = df['delta_t'] - df['delta_s_t']
        df['m_t'] = df['T_obs'] / df['Poblacion_10ymas_P']
        
        print(f"✓ Datos cargados exitosamente: {len(df)} años ({df['anio'].min()}-{df['anio'].max()})")
        print(f"  Población promedio: {df['Poblacion_10ymas_P'].mean():,.0f}")
        print(f"  Defunciones totales promedio: {df['defunciones_totales'].mean():,.0f}/año")
        print(f"  Defunciones por suicidio promedio: {df['defunciones_suicidio'].mean():,.0f}/año")
        print(f"  Población en tratamiento promedio: {df['T_obs'].mean():,.0f}")
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_excel}")
    except Exception as e:
        raise Exception(f"Error al cargar datos desde {ruta_excel}: {str(e)}")


def resumen_datos(df: pd.DataFrame) -> None:
    """
    Imprime un resumen estadístico de los datos cargados.
    
    Args:
        df: DataFrame con los datos del modelo
    """
    print("\n" + "="*60)
    print("RESUMEN DE DATOS")
    print("="*60)
    print(f"\nPeríodo: {df['anio'].min()} - {df['anio'].max()} ({len(df)} años)")
    print(f"\nEstadísticas de Población (P):")
    print(f"  Media: {df['Poblacion_10ymas_P'].mean():,.0f}")
    print(f"  Mínimo: {df['Poblacion_10ymas_P'].min():,.0f} ({df.loc[df['Poblacion_10ymas_P'].idxmin(), 'anio']:.0f})")
    print(f"  Máximo: {df['Poblacion_10ymas_P'].max():,.0f} ({df.loc[df['Poblacion_10ymas_P'].idxmax(), 'anio']:.0f})")
    
    print(f"\nEstadísticas de Defunciones Totales:")
    print(f"  Media: {df['defunciones_totales'].mean():,.0f}/año")
    print(f"  Mínimo: {df['defunciones_totales'].min():,} ({df.loc[df['defunciones_totales'].idxmin(), 'anio']:.0f})")
    print(f"  Máximo: {df['defunciones_totales'].max():,} ({df.loc[df['defunciones_totales'].idxmax(), 'anio']:.0f})")
    
    print(f"\nEstadísticas de Defunciones por Suicidio:")
    print(f"  Media: {df['defunciones_suicidio'].mean():,.1f}/año")
    print(f"  Mínimo: {df['defunciones_suicidio'].min()} ({df.loc[df['defunciones_suicidio'].idxmin(), 'anio']:.0f})")
    print(f"  Máximo: {df['defunciones_suicidio'].max()} ({df.loc[df['defunciones_suicidio'].idxmax(), 'anio']:.0f})")
    
    print(f"\nEstadísticas de Población en Tratamiento (T_obs):")
    print(f"  Media: {df['T_obs'].mean():,.0f}")
    print(f"  Mínimo: {df['T_obs'].min():,.0f} ({df.loc[df['T_obs'].idxmin(), 'anio']:.0f})")
    print(f"  Máximo: {df['T_obs'].max():,.0f} ({df.loc[df['T_obs'].idxmax(), 'anio']:.0f})")
    
    print(f"\nTasas calculadas:")
    print(f"  δ media: {df['delta_t'].mean():.6f}")
    print(f"  δ_s media: {df['delta_s_t'].mean():.6f}")
    print(f"  δ_n media: {df['delta_n_t'].mean():.6f}")
    print(f"  m media (aritmética): {df['m_t'].mean():.6f}")
    print("="*60 + "\n")
