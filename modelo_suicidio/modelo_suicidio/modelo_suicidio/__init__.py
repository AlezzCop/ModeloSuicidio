"""
Paquete para el Modelo No Lineal de Dinámica Poblacional del Suicidio.

Este paquete implementa el modelo matemático descrito en Granada et al. (2023)
para simular la dinámica poblacional del suicidio usando ecuaciones diferenciales ordinarias.

Módulos:
    - data_loader: Carga de datos desde archivos Excel
    - parameters: Definición y estimación de parámetros del modelo
    - model: Implementación del sistema de EDO
    - calibration: Calibración automática de parámetros
    - analysis: Condiciones iniciales y análisis de resultados
    - plots: Visualización de resultados
"""

from .data_loader import cargar_datos_excel
from .parameters import ModeloParametros, parametros_iniciales, estimar_tasas_defuncion, estimar_m, estimar_phi_psi
from .model import ModeloSuicidio
from .calibration import calibrar_parametros
from .analysis import condiciones_iniciales, prueba_escritorio
from .plots import plot_T_obs_vs_model, plot_series_completas, plot_compartimentos_stacked, plot_comparacion_calibracion

__version__ = '1.0.0'
__author__ = 'Granada et al., 2023 - Implementación Python'

__all__ = [
    'cargar_datos_excel',
    'ModeloParametros',
    'parametros_iniciales',
    'estimar_tasas_defuncion',
    'estimar_m',
    'estimar_phi_psi',
    'ModeloSuicidio',
    'calibrar_parametros',
    'condiciones_iniciales',
    'prueba_escritorio',
    'plot_T_obs_vs_model',
    'plot_series_completas',
    'plot_compartimentos_stacked',
    'plot_comparacion_calibracion',
]
