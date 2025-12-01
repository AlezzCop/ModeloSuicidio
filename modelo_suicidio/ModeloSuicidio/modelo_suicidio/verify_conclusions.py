import pandas as pd
import numpy as np
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelo_suicidio.core.parameters import ModeloParametros
from modelo_suicidio.core.statistics import calculate_statistics, generar_texto_conclusion_detallada

def test_conclusions():
    print("Testing conclusions generation...")
    
    # Create dummy data
    data = {
        'anio': range(2010, 2020),
        'T_obs': [100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
    }
    df = pd.DataFrame(data)
    
    # Define parameters
    params = ModeloParametros(
        delta=0.01,
        delta_s=0.001,
        delta_n=0.009,
        m=0.1,
        phi=0.5,
        psi=0.2,
        theta=0.05,
        rho=0.15,
        beta=0.2,
        gamma=0.01
    )
    
    # Mock prueba_escritorio by monkeypatching or just creating the result DF manually
    # Since calculate_statistics calls prueba_escritorio, we need to mock it or ensure it works.
    # However, importing it might be tricky if it has other dependencies.
    # Let's try to run calculate_statistics if possible, but if prueba_escritorio fails, we'll mock the result.
    
    # For this test, let's manually create the result DF that calculate_statistics would produce
    # and then call generar_texto_conclusion_detallada directly.
    
    res_df = df.copy()
    # Simulate a model that slightly overestimates
    res_df['T_model'] = res_df['T_obs'] * 1.05 
    
    stats = {
        'R2': 0.95,
        'MSE': 100.0,
        'RMSE': 10.0,
        'MAE': 8.0,
        'MAPE': 5.0,
        'n_obs': 10,
        'res_df': res_df
    }
    
    text = generar_texto_conclusion_detallada(stats, params, res_df, 2010, 2019)
    
    # Write to file to avoid console encoding issues
    output_file = "conclusions_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
        
    print(f"\nGenerated Text written to {output_file}")
    print("\nTest finished.")

if __name__ == "__main__":
    test_conclusions()
