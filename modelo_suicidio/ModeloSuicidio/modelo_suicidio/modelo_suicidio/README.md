# Modelo Dinámica Poblacional del Suicidio

Aplicación de escritorio en Python 3.11 y PyQt6 para simular y calibrar un modelo no lineal de dinámica poblacional del suicidio.

## Descripción del Modelo

El modelo considera tres compartimentos:
- **S(t)**: Población susceptible (vulnerable).
- **T(t)**: Población en tratamiento / ideación / intento.
- **R(t)**: Población recuperada.

Y una serie exógena **P(t)** (población vulnerable total).

## Estructura del Proyecto

- `core/`: Lógica matemática y de negocio.
    - `data_loader.py`: Carga de datos Excel.
    - `parameters.py`: Definición de parámetros.
    - `linear_relations.py`: Cálculos lineales iniciales.
    - `nonlinear_model.py`: Sistema de ecuaciones diferenciales.
    - `calibration.py`: Calibración por mínimos cuadrados.
- `ui/`: Interfaz gráfica (PyQt6).
    - `main_window.py`: Ventana principal.
    - `*_view.py`: Pestañas de la aplicación.

## Requisitos

- Python 3.11
- Ver `requirements.txt`

## Instalación

1. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

2. **Pestaña Datos**: Cargar el archivo Excel. Debe tener una hoja "Datos" con columnas: `anio`, `Poblacion_10ymas_P`, `defunciones_totales`, `defunciones_suicidio`, `T_obs`.

3. **Pestaña Parámetros**: Calcular los parámetros lineales base ($\delta, m, \phi, \psi$) y ajustar los valores iniciales de los no lineales ($\theta, \rho, \beta, \gamma$).

4. **Pestaña Simulación**: Correr el modelo con los parámetros actuales y visualizar las curvas $S, T, R$.

5. **Pestaña Calibración**: Ajustar automáticamente $\theta, \rho, \beta, \gamma$ para minimizar el error entre $T_{model}$ y $T_{obs}$.

## Formato Excel

El archivo debe contener una hoja llamada `Datos` con las columnas:
- `anio`
- `Poblacion_10ymas_P`
- `defunciones_totales`
- `defunciones_suicidio`
- `T_obs`
