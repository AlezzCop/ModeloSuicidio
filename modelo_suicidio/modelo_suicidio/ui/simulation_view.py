from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QMessageBox, QCheckBox)
from .matplotlib_widget import MatplotlibWidget
import numpy as np

class SimulationView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.spin_start = QSpinBox()
        self.spin_start.setRange(1900, 2100)
        self.spin_end = QSpinBox()
        self.spin_end.setRange(1900, 2100)
        
        self.btn_sim = QPushButton("Simular Modelo No Lineal")
        self.btn_sim.clicked.connect(self.run_simulation)
        
        controls_layout.addWidget(QLabel("Año Inicio:"))
        controls_layout.addWidget(self.spin_start)
        controls_layout.addWidget(QLabel("Año Fin:"))
        controls_layout.addWidget(self.spin_end)
        controls_layout.addWidget(self.btn_sim)
        controls_layout.addStretch()
        
        self.layout.addLayout(controls_layout)
        
        self.layout.addLayout(controls_layout)
        
        # Gráfico 1: Dinámica Poblacional
        self.plot_dynamics = MatplotlibWidget()
        self.layout.addWidget(self.plot_dynamics)
        
        # Gráfico 2: Ajuste T(t)
        self.plot_fit = MatplotlibWidget()
        self.layout.addWidget(self.plot_fit)

    def set_years(self, min_y, max_y):
        self.spin_start.setValue(min_y)
        self.spin_end.setValue(max_y)

    def run_simulation(self):
        try:
            # Actualizar parámetros manuales antes de simular
            self.main_window.update_nonlinear_params_from_ui()
            
            res_df = self.main_window.run_simulation(
                self.spin_start.value(),
                self.spin_end.value()
            )
            
            self.plot_results(res_df)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def plot_results(self, res_df):
        # --- Gráfico 1: Dinámica Poblacional ---
        fig1 = self.plot_dynamics.get_figure()
        fig1.clear()
        
        ax1 = fig1.add_subplot(111)
        ax1.plot(res_df['anio'], res_df['S_model'], label='S(t)', color='blue')
        ax1.plot(res_df['anio'], res_df['T_model'], label='T(t)', color='orange')
        ax1.plot(res_df['anio'], res_df['R_model'], label='R(t)', color='green')
        
        # P(t) también para referencia
        if self.main_window.df is not None:
             mask = (self.main_window.df['anio'] >= res_df['anio'].min()) & \
                    (self.main_window.df['anio'] <= res_df['anio'].max())
             sub = self.main_window.df[mask]
             ax1.plot(sub['anio'], sub['Poblacion_10ymas_P'], 'k--', label='P(t) data', alpha=0.5)

        ax1.set_title("Dinámica Poblacional (Modelo No Lineal)")
        ax1.legend()
        ax1.grid(True)
        
        desc1 = "Esta gráfica muestra la evolución de los compartimentos S(t), T(t) y R(t) a lo largo del tiempo. La línea azul representa la población susceptible, la línea naranja muestra la población en tratamiento, y la línea verde muestra a los recuperados. Los datos de la población vulnerable (P(t)) se muestran en la línea gris punteada."
        self.plot_dynamics.set_description(desc1)
        self.plot_dynamics.draw()
        
        # --- Gráfico 2: Ajuste T(t) ---
        fig2 = self.plot_fit.get_figure()
        fig2.clear()
        
        ax2 = fig2.add_subplot(111)
        ax2.plot(res_df['anio'], res_df['T_model'], 'b-', label='T Modelo')
        
        if 'T_obs' in res_df.columns:
            valid = res_df.dropna(subset=['T_obs'])
            ax2.plot(valid['anio'], valid['T_obs'], 'ro', label='T Observado')
            
        ax2.set_title("Ajuste T(t)")
        ax2.set_xlabel("Año")
        ax2.legend()
        ax2.grid(True)
        
        desc2 = "En esta gráfica, se compara el modelo T(t) (línea azul) con los datos observados T_obs (puntos rojos). La comparación muestra cómo el modelo simula la dinámica de los casos en tratamiento en comparación con los datos reales."
        self.plot_fit.set_description(desc2)
        self.plot_fit.draw()
