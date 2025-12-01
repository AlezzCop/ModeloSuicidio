from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QDoubleSpinBox, QGroupBox, QFormLayout, QSpinBox, QMessageBox)
from .matplotlib_widget import MatplotlibWidget

class ParametersView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        
        # Panel de control
        control_layout = QHBoxLayout()
        
        # Grupo 1: Rango de calibración lineal
        grp_range = QGroupBox("Rango Estimación Lineal")
        range_layout = QFormLayout()
        self.spin_year_start = QSpinBox()
        self.spin_year_start.setRange(1900, 2100)
        self.spin_year_end = QSpinBox()
        self.spin_year_end.setRange(1900, 2100)
        
        range_layout.addRow("Año Inicio:", self.spin_year_start)
        range_layout.addRow("Año Fin:", self.spin_year_end)
        
        self.btn_calc_linear = QPushButton("Calcular Parámetros Lineales")
        self.btn_calc_linear.clicked.connect(self.calc_linear_params)
        range_layout.addRow(self.btn_calc_linear)
        
        grp_range.setLayout(range_layout)
        control_layout.addWidget(grp_range)
        
        # Grupo 2: Parámetros Lineales (Solo lectura o ajuste fino)
        grp_linear = QGroupBox("Parámetros Lineales")
        linear_layout = QFormLayout()
        
        self.lbl_delta = QLabel("0.0")
        self.lbl_delta_s = QLabel("0.0")
        self.lbl_delta_n = QLabel("0.0")
        self.lbl_m = QLabel("0.0")
        
        self.spin_phi = QDoubleSpinBox()
        self.spin_phi.setRange(0.0, 1.0)
        self.spin_phi.setSingleStep(0.01)
        self.spin_phi.setValue(0.5)
        self.spin_phi.valueChanged.connect(self.update_psi)
        
        self.lbl_psi = QLabel("0.0")
        
        linear_layout.addRow("δ (Def. Total):", self.lbl_delta)
        linear_layout.addRow("δ_s (Suicidio):", self.lbl_delta_s)
        linear_layout.addRow("δ_n (No Suicidio):", self.lbl_delta_n)
        linear_layout.addRow("m (Tasa Trat.):", self.lbl_m)
        linear_layout.addRow("φ (Prop. R):", self.spin_phi)
        linear_layout.addRow("ψ (Prop. S):", self.lbl_psi)
        
        grp_linear.setLayout(linear_layout)
        control_layout.addWidget(grp_linear)
        
        # Grupo 3: Parámetros No Lineales (Iniciales)
        grp_nolinear = QGroupBox("Parámetros No Lineales (Iniciales)")
        nolinear_layout = QFormLayout()
        
        self.spin_theta = QDoubleSpinBox()
        self.spin_theta.setDecimals(6)
        self.spin_theta.setRange(0.0, 1.0)
        self.spin_theta.setSingleStep(0.01)
        self.spin_theta.setValue(0.1)
        
        self.spin_rho = QDoubleSpinBox()
        self.spin_rho.setDecimals(6)
        self.spin_rho.setRange(0.0, 1.0)
        self.spin_rho.setSingleStep(0.01)
        self.spin_rho.setValue(0.5)
        
        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setDecimals(6)
        self.spin_beta.setRange(0.0, 1.0)
        self.spin_beta.setSingleStep(0.01)
        self.spin_beta.setValue(0.5)
        
        self.spin_gamma = QDoubleSpinBox()
        self.spin_gamma.setDecimals(6)
        self.spin_gamma.setRange(0.0, 20.0)
        self.spin_gamma.setSingleStep(0.1)
        self.spin_gamma.setValue(1.0)
        
        nolinear_layout.addRow("θ (Flujo P->S):", self.spin_theta)
        nolinear_layout.addRow("ρ (T->R):", self.spin_rho)
        nolinear_layout.addRow("β (Influencia):", self.spin_beta)
        nolinear_layout.addRow("γ (Otras causas):", self.spin_gamma)
        
        grp_nolinear.setLayout(nolinear_layout)
        control_layout.addWidget(grp_nolinear)
        
        self.layout.addLayout(control_layout)
        
        # Botón series lineales
        self.btn_series_lin = QPushButton("Construir Series Lineales (S_lin, T_lin, R_lin)")
        self.btn_series_lin.clicked.connect(self.build_linear_series)
        self.layout.addWidget(self.btn_series_lin)
        
        # Gráfico
        self.plot_widget = MatplotlibWidget()
        self.layout.addWidget(self.plot_widget)

    def set_years(self, min_y, max_y):
        self.spin_year_start.setValue(min_y)
        self.spin_year_end.setValue(max_y)

    def calc_linear_params(self):
        try:
            self.main_window.calculate_linear_parameters(
                self.spin_year_start.value(),
                self.spin_year_end.value()
            )
            self.update_display_params()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_psi(self):
        # Recalcular psi si cambia phi
        if self.main_window.params:
            self.main_window.params.phi = self.spin_phi.value()
            # psi = 1 - m - phi*m
            m = self.main_window.params.m
            self.main_window.params.psi = 1.0 - m - self.main_window.params.phi * m
            self.lbl_psi.setText(f"{self.main_window.params.psi:.4f}")

    def update_display_params(self):
        p = self.main_window.params
        if p:
            self.lbl_delta.setText(f"{p.delta:.6f}")
            self.lbl_delta_s.setText(f"{p.delta_s:.6f}")
            self.lbl_delta_n.setText(f"{p.delta_n:.6f}")
            self.lbl_m.setText(f"{p.m:.6f}")
            self.spin_phi.blockSignals(True)
            self.spin_phi.setValue(p.phi)
            self.spin_phi.blockSignals(False)
            self.lbl_psi.setText(f"{p.psi:.6f}")
            
            self.spin_theta.setValue(p.theta)
            self.spin_rho.setValue(p.rho)
            self.spin_beta.setValue(p.beta)
            self.spin_gamma.setValue(p.gamma)

    def get_nonlinear_params(self):
        return {
            'theta': self.spin_theta.value(),
            'rho': self.spin_rho.value(),
            'beta': self.spin_beta.value(),
            'gamma': self.spin_gamma.value()
        }

    def build_linear_series(self):
        try:
            self.main_window.build_linear_series()
            self.plot_linear_series()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def plot_linear_series(self):
        df = self.main_window.df
        if df is not None and 'S_lin' in df.columns:
            fig = self.plot_widget.get_figure()
            fig.clear()
            ax = fig.add_subplot(111)
            
            ax.plot(df['anio'], df['S_lin'], label='S_lin')
            ax.plot(df['anio'], df['T_lin'], label='T_lin')
            ax.plot(df['anio'], df['R_lin'], label='R_lin')
            ax.set_title("Series Lineales Aproximadas")
            ax.set_xlabel("Año")
            ax.legend()
            ax.grid(True)
            
            self.plot_widget.draw()
            
            # Agregar descripción
            desc = "<b>Series Lineales Aproximadas:</b><br>"
            desc += "Esta gráfica muestra las aproximaciones lineales para los compartimentos S(t) (susceptibles), T(t) (en tratamiento) y R(t) (recuperados). La línea azul muestra la evolución de la población susceptible, la línea naranja representa la cantidad de personas en tratamiento, y la línea verde muestra el número de personas recuperadas. Estas aproximaciones se generan con los parámetros calculados para el rango de años seleccionado."
            
            self.plot_widget.set_description(desc)
