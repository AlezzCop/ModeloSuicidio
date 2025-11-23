# Modelo No Lineal de Dinámica Poblacional del Suicidio

Implementación en Python 3.11 del modelo matemático descrito en el artículo "Modelo no lineal de la interacción dinámica poblacional del suicidio" (Granada et al., 2023).

## Descripción del Modelo

El modelo implementa un sistema de ecuaciones diferenciales ordinarias (EDO) con tres compartimentos poblacionales:

- **S(t)**: Población susceptible (vulnerable a suicidio)
- **T(t)**: Población en tratamiento (ideación o intento)
- **R(t)**: Población recuperada

Además, el modelo usa como entrada exógena:
- **P(t)**: Población total vulnerable (≥ 10 años)

### Ecuaciones del Modelo

El sistema de EDO implementado (ecuación 9 del artículo) es:

```
dS/dt = θP(t) + (1-δₙ)R - γ(1-β)δₛS - βδₛ(T/P)S - δₛS - δₙS
dT/dt = γ(1-β)δₛS + βδₛ(T/P)S - ρT - δₛT - δₙT
dR/dt = ρT - R
```

Donde:
- **θ**: Tasa de paso de vulnerable a susceptible
- **ρ**: Tasa de recuperación (salida de T hacia R)
- **β**: Proporción de entrada a T por influencia/contagio
- **γ**: Factor de proporción para entrada a T por otras causas
- **δ**: Tasa de defunción total
- **δₛ**: Tasa de defunción por suicidio
- **δₙ**: Tasa de defunción por otras causas (δₙ = δ - δₛ)
- **m**: Tasa global de tratamiento (media geométrica de T/P)
- **φ**: Proporción de T que pasa a R
- **ψ**: Proporción de P que está en S (relación: ψ = 1 - m - φm)

## Instalación

### Requisitos

- Python 3.11 o superior

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Formato del Archivo Excel

El archivo Excel debe contener las siguientes columnas (una fila por año):

- `anio` (int): Año de la observación
- `Poblacion_10ymas_P` (float): Población vulnerable ≥ 10 años [P(t)]
- `defunciones_totales` (int): Total de defunciones ese año
- `defunciones_suicidio` (int): Defunciones por suicidio ese año
- `T_obs` (float): Población en tratamiento observada (casos de intento/ideación)

Ejemplo:

| anio | Poblacion_10ymas_P | defunciones_totales | defunciones_suicidio | T_obs |
|------|-------------------|---------------------|---------------------|-------|
| 2010 | 2500000 | 15000 | 150 | 5000 |
| 2011 | 2550000 | 15200 | 155 | 5100 |
| ... | ... | ... | ... | ... |

## Uso

### Ejecución Básica

```bash
python main.py
```

El programa solicitará la ruta del archivo Excel con los datos. Si no se proporciona, intentará usar `datos_oaxaca.xlsx` en el directorio actual.

### Flujo del Programa

1. **Carga de datos**: Lee el archivo Excel con los datos de Oaxaca
2. **Estimación de parámetros básicos**:
   - Calcula tasas de defunción (δ, δₛ, δₙ)
   - Estima tasa de tratamiento m (media geométrica)
   - Calcula φ y ψ
3. **Condiciones iniciales**: Calcula S₀, T₀, R₀ desde el primer año
4. **Prueba de escritorio**: Simula el modelo y compara con datos observados
5. **Calibración (opcional)**: Ajusta parámetros θ, ρ, β, γ para minimizar error
6. **Resultados**: Genera CSV y gráficas PNG

### Salidas

El programa genera:

- `resultados_modelo.csv`: Tabla con años, valores observados vs simulados, errores
- `comparacion_T.png`: Gráfica de T_obs vs T_model
- `series_completas.png`: Evolución temporal de S(t), T(t), R(t), P(t)

## Estructura del Paquete

```
modelo_suicidio/
├── __init__.py           # Inicialización del paquete
├── data_loader.py        # Carga de datos desde Excel
├── parameters.py         # Clase y funciones para parámetros
├── model.py             # Sistema de EDO
├── calibration.py       # Calibración de parámetros
├── analysis.py          # Condiciones iniciales y prueba de escritorio
└── plots.py             # Funciones de visualización
```

## Ejemplo de Uso Programático

```python
from modelo_suicidio import cargar_datos_excel, parametros_iniciales, ModeloSuicidio
from modelo_suicidio import condiciones_iniciales, prueba_escritorio
import matplotlib.pyplot as plt

# Cargar datos
df = cargar_datos_excel("datos_oaxaca.xlsx")

# Estimar parámetros
params = parametros_iniciales(df)

# Crear modelo
modelo = ModeloSuicidio(params, df['Poblacion_10ymas_P'], df['anio'])

# Condiciones iniciales
x0 = condiciones_iniciales(df, params)

# Simular
t, S, T, R = modelo.simular(df['anio'].iloc[0], df['anio'].iloc[-1], x0)

# Graficar
plt.plot(t, T)
plt.xlabel('Año')
plt.ylabel('Población en Tratamiento')
plt.show()
```

## Referencia

Granada, J. R., et al. (2023). "Modelo no lineal de la interacción dinámica poblacional del suicidio". 

## Licencia

Este proyecto es de código abierto y está disponible para uso académico y de investigación.

## Contacto

Para preguntas o sugerencias sobre este modelo, consulte el artículo original.
