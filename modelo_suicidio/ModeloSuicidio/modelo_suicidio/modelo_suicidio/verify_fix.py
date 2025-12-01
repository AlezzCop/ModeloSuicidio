import pandas as pd
import numpy as np
from core.parameters import ModeloParametros
from core.linear_relations import estimar_tasas_defuncion, estimar_m, calcular_phi_psi
from core.calibration import calibrar_parametros
from core.analysis import prueba_escritorio

def verify():
    print("Cargando datos...")
    df = pd.read_excel('Simulacion.xlsx', sheet_name='Datos')
    
    anio_ini = 2010
    anio_fin = 2020
    
    print("Calculando parámetros lineales...")
    delta, delta_s, delta_n = estimar_tasas_defuncion(df, anio_ini, anio_fin)
    m = estimar_m(df, anio_ini, anio_fin)
    phi, psi = calcular_phi_psi(m, 0.5)
    
    params = ModeloParametros(
        delta=delta, delta_s=delta_s, delta_n=delta_n,
        m=m, phi=phi, psi=psi,
        theta=0.1, rho=0.5, beta=0.5, gamma=1.0 # Valores dummy iniciales
    )
    
    print(f"Params lineales: delta={delta:.5f}, m={m:.5f}, psi={psi:.5f}")
    
    print("Iniciando calibración...")
    params_cal, cost, log = calibrar_parametros(df, params, anio_ini, anio_fin)
    
    print(log)
    print("Parámetros calibrados:")
    print(f"Theta: {params_cal.theta}")
    print(f"Rho: {params_cal.rho}")
    print(f"Beta: {params_cal.beta}")
    print(f"Gamma: {params_cal.gamma}")
    
    print("Corriendo prueba de escritorio con calibrados...")
    res = prueba_escritorio(df, params_cal, anio_ini, anio_fin)
    print(res[['anio', 'T_obs', 'T_model', 'error_rel']])

if __name__ == "__main__":
    verify()
