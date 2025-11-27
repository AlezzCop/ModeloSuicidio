"""
Módulo para visualización de resultados del modelo.

Provee funciones para graficar series temporales, comparaciones
entre datos observados y modelo, y análisis de resultados.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Callable, Optional
import matplotlib.dates as mdates


def configurar_estilo():
    """
    Configura el estilo por defecto de matplotlib para las gráficas.
    """
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['legend.fontsize'] = 9
    

def plot_T_obs_vs_model(
    df_resultados: pd.DataFrame,
    titulo: str = "Comparación: T observado vs T modelo",
    guardar_como: Optional[str] = None,
    mostrar: bool = True
) -> None:
    """
    Grafica la comparación entre T_obs y T_model.
    
    Args:
        df_resultados: DataFrame generado por prueba_escritorio() con columnas
                      'anio', 'T_obs', 'T_model'
        titulo: Título de la gráfica
        guardar_como: Ruta donde guardar la figura (opcional)
        mostrar: Si True, muestra la figura con plt.show()
    """
    configurar_estilo()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Gráfica superior: T_obs vs T_model
    ax1.plot(df_resultados['anio'], df_resultados['T_obs'], 
             'o-', label='T observado', color='#2E86AB', markersize=6, linewidth=2)
    ax1.plot(df_resultados['anio'], df_resultados['T_model'], 
             's--', label='T modelo', color='#A23B72', markersize=5, linewidth=2, alpha=0.8)
    
    ax1.set_xlabel('Año')
    ax1.set_ylabel('Población en Tratamiento')
    ax1.set_title(titulo)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Formatear el eje y con separadores de miles
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Gráfica inferior: Error relativo
    ax2.bar(df_resultados['anio'], df_resultados['error_rel_pct'], 
            color='#F18F01', alpha=0.7, label='Error relativo')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    ax2.set_xlabel('Año')
    ax2.set_ylabel('Error Relativo (%)')
    ax2.set_title('Error Relativo: (T_model - T_obs) / T_obs × 100')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if guardar_como:
        plt.savefig(guardar_como, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfica guardada en: {guardar_como}")
    
    if mostrar:
        plt.show()
    else:
        plt.close()


def plot_series_completas(
    t: np.ndarray,
    S: np.ndarray,
    T: np.ndarray,
    R: np.ndarray,
    P_func: Callable[[float], float],
    titulo: str = "Evolución Temporal del Modelo",
    guardar_como: Optional[str] = None,
    mostrar: bool = True
) -> None:
    """
    Grafica la evolución temporal de S(t), T(t), R(t) y P(t).
    
    Similar a la figura 2 del artículo Granada et al. (2023).
    
    Args:
        t: Array de tiempos (años)
        S: Array de valores de S(t)
        T: Array de valores de T(t)
        R: Array de valores de R(t)
        P_func: Función que devuelve P(t) dado t
        titulo: Título de la gráfica
        guardar_como: Ruta donde guardar la figura (opcional)
        mostrar: Si True, muestra la figura con plt.show()
    """
    configurar_estilo()
    
    # Calcular P(t) para todos los tiempos
    P = np.array([P_func(ti) for ti in t])
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Graficar las cuatro series
    ax.plot(t, P, '-', label='P(t) - Población Vulnerable', 
            color='#264653', linewidth=2.5)
    ax.plot(t, S, '-', label='S(t) - Susceptibles', 
            color='#2A9D8F', linewidth=2)
    ax.plot(t, T, '-', label='T(t) - En Tratamiento', 
            color='#E76F51', linewidth=2)
    ax.plot(t, R, '-', label='R(t) - Recuperados', 
            color='#F4A261', linewidth=2)
    
    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel('Población', fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Formatear el eje y con separadores de miles
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Añadir anotación con verificación de conservación
    # En el último punto verificar que S + T + R ≈ P
    idx_final = -1
    suma_final = S[idx_final] + T[idx_final] + R[idx_final]
    P_final = P[idx_final]
    error_conservacion = abs(suma_final - P_final) / P_final * 100
    
    textstr = f'Verificación (t={t[idx_final]:.1f}):\n'
    textstr += f'S+T+R = {suma_final:,.0f}\n'
    textstr += f'P = {P_final:,.0f}\n'
    textstr += f'Error: {error_conservacion:.2f}%'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    if guardar_como:
        plt.savefig(guardar_como, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfica guardada en: {guardar_como}")
    
    if mostrar:
        plt.show()
    else:
        plt.close()


def plot_compartimentos_stacked(
    t: np.ndarray,
    S: np.ndarray,
    T: np.ndarray,
    R: np.ndarray,
    titulo: str = "Composición Poblacional (S + T + R)",
    guardar_como: Optional[str] = None,
    mostrar: bool = True
) -> None:
    """
    Grafica los compartimentos S, T, R como áreas apiladas.
    
    Args:
        t: Array de tiempos
        S: Array de S(t)
        T: Array de T(t)
        R: Array de R(t)
        titulo: Título de la gráfica
        guardar_como: Ruta donde guardar
        mostrar: Si mostrar la figura
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Gráfica de áreas apiladas
    ax.fill_between(t, 0, S, label='S - Susceptibles', color='#2A9D8F', alpha=0.7)
    ax.fill_between(t, S, S+T, label='T - En Tratamiento', color='#E76F51', alpha=0.7)
    ax.fill_between(t, S+T, S+T+R, label='R - Recuperados', color='#F4A261', alpha=0.7)
    
    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel('Población', fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Formatear eje y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    plt.tight_layout()
    
    if guardar_como:
        plt.savefig(guardar_como, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfica guardada en: {guardar_como}")
    
    if mostrar:
        plt.show()
    else:
        plt.close()


def plot_comparacion_calibracion(
    df_resultados_inicial: pd.DataFrame,
    df_resultados_calibrado: pd.DataFrame,
    titulo: str = "Comparación: Parámetros Iniciales vs Calibrados",
    guardar_como: Optional[str] = None,
    mostrar: bool = True
) -> None:
    """
    Compara los resultados antes y después de calibración.
    
    Args:
        df_resultados_inicial: Resultados con parámetros iniciales
        df_resultados_calibrado: Resultados con parámetros calibrados
        titulo: Título de la gráfica
        guardar_como: Ruta donde guardar
        mostrar: Si mostrar la figura
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Datos observados
    ax.plot(df_resultados_inicial['anio'], df_resultados_inicial['T_obs'], 
            'o-', label='T observado', color='black', markersize=7, linewidth=2.5)
    
    # Modelo con parámetros iniciales
    ax.plot(df_resultados_inicial['anio'], df_resultados_inicial['T_model'], 
            's--', label='T modelo (inicial)', color='#E63946', markersize=5, linewidth=2, alpha=0.7)
    
    # Modelo con parámetros calibrados
    ax.plot(df_resultados_calibrado['anio'], df_resultados_calibrado['T_model'], 
            '^-', label='T modelo (calibrado)', color='#06A77D', markersize=5, linewidth=2, alpha=0.8)
    
    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel('Población en Tratamiento', fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Formatear eje y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Calcular y mostrar métricas
    from .analysis import calcular_metricas
    
    metricas_inicial = calcular_metricas(
        df_resultados_inicial['T_obs'].values,
        df_resultados_inicial['T_model'].values
    )
    
    metricas_calibrado = calcular_metricas(
        df_resultados_calibrado['T_obs'].values,
        df_resultados_calibrado['T_model'].values
    )
    
    textstr = 'Métricas:\n'
    textstr += f'MAPE inicial: {metricas_inicial["MAPE"]:.2f}%\n'
    textstr += f'MAPE calibrado: {metricas_calibrado["MAPE"]:.2f}%\n'
    textstr += f'R² inicial: {metricas_inicial["R2"]:.4f}\n'
    textstr += f'R² calibrado: {metricas_calibrado["R2"]:.4f}'
    
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    if guardar_como:
        plt.savefig(guardar_como, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfica guardada en: {guardar_como}")
    
    if mostrar:
        plt.show()
    else:
        plt.close()
