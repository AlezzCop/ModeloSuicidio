"""
Script principal para ejecutar el modelo de dinámica poblacional del suicidio.

Interfaz de línea de comandos que permite:
1. Cargar datos desde Excel
2. Estimar parámetros iniciales
3. Ejecutar prueba de escritorio
4. Calibrar parámetros (opcional)
5. Generar y guardar resultados y gráficas

Uso:
    python main.py
"""

import os
import sys
from pathlib import Path

# Importar módulos del paquete
from modelo_suicidio import (
    cargar_datos_excel,
    parametros_iniciales,
    ModeloSuicidio,
    condiciones_iniciales,
    prueba_escritorio,
    calibrar_parametros,
    plot_T_obs_vs_model,
    plot_series_completas,
    plot_compartimentos_stacked,
    plot_comparacion_calibracion
)
from modelo_suicidio.data_loader import resumen_datos
from modelo_suicidio.analysis import comparar_parametros


def solicitar_ruta_excel() -> str:
    """
    Solicita al usuario la ruta del archivo Excel.
    
    Returns:
        Ruta al archivo Excel
    """
    print("\n" + "="*70)
    print("MODELO NO LINEAL DE DINÁMICA POBLACIONAL DEL SUICIDIO")
    print("Granada et al., 2023 - Implementación en Python 3.11")
    print("="*70)
    
    print("\nPor favor, ingrese la ruta del archivo Excel con los datos.")
    print("(Presione Enter para usar 'datos_oaxaca.xlsx' en el directorio actual)")
    
    ruta = input("\nRuta del archivo Excel: ").strip()
    
    if not ruta:
        ruta = "datos_oaxaca.xlsx"
        print(f"Usando ruta por defecto: {ruta}")
    
    # Quitar comillas si el usuario las incluyó
    ruta = ruta.strip('"').strip("'")
    
    return ruta


def preguntar_si_no(pregunta: str, por_defecto: bool = True) -> bool:
    """
    Hace una pregunta sí/no al usuario.
    
    Args:
        pregunta: Texto de la pregunta
        por_defecto: Valor por defecto si el usuario solo presiona Enter
    
    Returns:
        True si la respuesta es 'sí', False si es 'no'
    """
    sufijo = " [S/n]: " if por_defecto else " [s/N]: "
    
    while True:
        respuesta = input(pregunta + sufijo).strip().lower()
        
        if not respuesta:
            return por_defecto
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print("Por favor, responda 's' (sí) o 'n' (no).")


def main():
    """
    Función principal del programa.
    """
    try:
        # 1. Solicitar ruta del archivo Excel
        ruta_excel = solicitar_ruta_excel()
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_excel):
            print(f"\n❌ Error: El archivo '{ruta_excel}' no existe.")
            print("Por favor, verifique la ruta y vuelva a intentar.")
            sys.exit(1)
        
        # 2. Cargar datos
        print("\n" + "─"*70)
        print("CARGANDO DATOS...")
        print("─"*70)
        
        df = cargar_datos_excel(ruta_excel)
        
        # Mostrar resumen
        if preguntar_si_no("\n¿Desea ver un resumen detallado de los datos?", por_defecto=False):
            resumen_datos(df)
        
        # 3. Estimar parámetros iniciales
        print("\n" + "─"*70)
        print("ESTIMANDO PARÁMETROS INICIALES...")
        print("─"*70)
        
        # Preguntar valores iniciales para parámetros a calibrar
        print("\nSe usarán los siguientes valores iniciales para los parámetros a calibrar:")
        print("  θ (theta) = 0.01  - Tasa de paso de vulnerable a susceptible")
        print("  ρ (rho)   = 0.1   - Tasa de recuperación")
        print("  β (beta)  = 0.3   - Proporción por influencia/contagio")
        print("  γ (gamma) = 0.7   - Factor de otras causas")
        
        usar_defecto = preguntar_si_no("\n¿Desea usar estos valores por defecto?", por_defecto=True)
        
        if usar_defecto:
            params_iniciales = parametros_iniciales(df)
        else:
            try:
                theta = float(input("Ingrese θ (theta): "))
                rho = float(input("Ingrese ρ (rho): "))
                beta = float(input("Ingrese β (beta, entre 0 y 1): "))
                gamma = float(input("Ingrese γ (gamma): "))
                params_iniciales = parametros_iniciales(df, theta=theta, rho=rho, beta=beta, gamma=gamma)
            except ValueError:
                print("Valor inválido. Usando valores por defecto.")
                params_iniciales = parametros_iniciales(df)
        
        print("\n" + params_iniciales.__str__())
        
        # 4. Ejecutar prueba de escritorio
        print("\n" + "─"*70)
        print("EJECUTANDO PRUEBA DE ESCRITORIO...")
        print("─"*70)
        
        resultados_inicial = prueba_escritorio(df, params_iniciales, verbose=True)
        
        # 5. Guardar resultados iniciales
        archivo_csv = "resultados_modelo_inicial.csv"
        resultados_inicial.to_csv(archivo_csv, index=False)
        print(f"\n✓ Resultados guardados en: {archivo_csv}")
        
        # 6. Generar gráficas iniciales
        print("\n" + "─"*70)
        print("GENERANDO GRÁFICAS...")
        print("─"*70)
        
        plot_T_obs_vs_model(
            resultados_inicial,
            titulo="Comparación: T observado vs T modelo (Parámetros Iniciales)",
            guardar_como="comparacion_T_inicial.png",
            mostrar=False
        )
        
        # Graficar series completas
        modelo = ModeloSuicidio(params_iniciales, df['Poblacion_10ymas_P'], df['anio'])
        x0 = condiciones_iniciales(df, params_iniciales)
        t, S, T, R = modelo.simular(df['anio'].iloc[0], df['anio'].iloc[-1], x0, num_pasos=300)
        
        plot_series_completas(
            t, S, T, R,
            lambda ti: modelo.P_t(ti),
            titulo="Evolución Temporal del Modelo (Parámetros Iniciales)",
            guardar_como="series_completas_inicial.png",
            mostrar=False
        )
        
        plot_compartimentos_stacked(
            t, S, T, R,
            titulo="Composición Poblacional S+T+R (Parámetros Iniciales)",
            guardar_como="compartimentos_inicial.png",
            mostrar=False
        )
        
        # 7. Preguntar si desea calibrar
        if preguntar_si_no("\n¿Desea calibrar los parámetros?", por_defecto=True):
            print("\n" + "─"*70)
            print("INICIANDO CALIBRACIÓN...")
            print("─"*70)
            print("\nEsto puede tardar algunos minutos dependiendo del tamaño de los datos.")
            
            try:
                params_calibrados, resultado_opt = calibrar_parametros(
                    df,
                    params_iniciales,
                    metodo='trf',
                    verbose=1
                )
                
                # Comparar parámetros
                comparar_parametros(params_iniciales, params_calibrados)
                
                # Ejecutar prueba de escritorio con parámetros calibrados
                print("\n" + "─"*70)
                print("PRUEBA DE ESCRITORIO CON PARÁMETROS CALIBRADOS...")
                print("─"*70)
                
                resultados_calibrado = prueba_escritorio(df, params_calibrados, verbose=True)
                
                # Guardar resultados calibrados
                archivo_csv_calibrado = "resultados_modelo_calibrado.csv"
                resultados_calibrado.to_csv(archivo_csv_calibrado, index=False)
                print(f"\n✓ Resultados calibrados guardados en: {archivo_csv_calibrado}")
                
                # Generar gráficas con parámetros calibrados
                print("\n" + "─"*70)
                print("GENERANDO GRÁFICAS CON PARÁMETROS CALIBRADOS...")
                print("─"*70)
                
                plot_T_obs_vs_model(
                    resultados_calibrado,
                    titulo="Comparación: T observado vs T modelo (Parámetros Calibrados)",
                    guardar_como="comparacion_T_calibrado.png",
                    mostrar=False
                )
                
                # Graficar series completas calibradas
                modelo_cal = ModeloSuicidio(params_calibrados, df['Poblacion_10ymas_P'], df['anio'])
                x0_cal = condiciones_iniciales(df, params_calibrados)
                t_cal, S_cal, T_cal, R_cal = modelo_cal.simular(
                    df['anio'].iloc[0], df['anio'].iloc[-1], x0_cal, num_pasos=300
                )
                
                plot_series_completas(
                    t_cal, S_cal, T_cal, R_cal,
                    lambda ti: modelo_cal.P_t(ti),
                    titulo="Evolución Temporal del Modelo (Parámetros Calibrados)",
                    guardar_como="series_completas_calibrado.png",
                    mostrar=False
                )
                
                # Comparación inicial vs calibrado
                plot_comparacion_calibracion(
                    resultados_inicial,
                    resultados_calibrado,
                    titulo="Comparación: Parámetros Iniciales vs Calibrados",
                    guardar_como="comparacion_inicial_vs_calibrado.png",
                    mostrar=False
                )
                
            except Exception as e:
                print(f"\n❌ Error durante la calibración: {e}")
                print("Continuando con los parámetros iniciales.")
        
        # 8. Resumen final
        print("\n" + "="*70)
        print("EJECUCIÓN COMPLETADA CON ÉXITO")
        print("="*70)
        print("\nArchivos generados:")
        
        archivos_generados = [
            "resultados_modelo_inicial.csv",
            "comparacion_T_inicial.png",
            "series_completas_inicial.png",
            "compartimentos_inicial.png"
        ]
        
        if os.path.exists("resultados_modelo_calibrado.csv"):
            archivos_generados.extend([
                "resultados_modelo_calibrado.csv",
                "comparacion_T_calibrado.png",
                "series_completas_calibrado.png",
                "comparacion_inicial_vs_calibrado.png"
            ])
        
        for i, archivo in enumerate(archivos_generados, 1):
            if os.path.exists(archivo):
                print(f"  {i}. {archivo}")
        
        print("\n" + "="*70)
        print("Gracias por usar el modelo de dinámica poblacional del suicidio.")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
