from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from core.data_loader import cargar_datos_excel
from core.parameters import ModeloParametros
from core.linear_relations import estimar_tasas_defuncion, estimar_m, calcular_phi_psi, construir_series_lineales
from core.analysis import prueba_escritorio

from .data_view import DataView
from .parameters_view import ParametersView
from .simulation_view import SimulationView
from .calibration_view import CalibrationView
from .conclusions_view import ConclusionsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modelo Dinámica Poblacional del Suicidio")
        self.resize(1000, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Inicializar vistas
        self.ui_data = DataView(self)
        self.ui_parameters = ParametersView(self)
        self.ui_simulation = SimulationView(self)
        self.ui_calibration = CalibrationView(self)
        self.ui_conclusions = ConclusionsView(self)
        
        self.tabs.addTab(self.ui_data, "Datos")
        self.tabs.addTab(self.ui_parameters, "Parámetros")
        self.tabs.addTab(self.ui_simulation, "Simulación")
        self.tabs.addTab(self.ui_calibration, "Calibración")
        self.tabs.addTab(self.ui_conclusions, "Conclusiones")
        
        # Estado del modelo
        self.df = None
        self.params = None

    def load_data(self, path):
        self.df = cargar_datos_excel(path)
        
        # Configurar rangos por defecto en las vistas
        min_y = int(self.df['anio'].min())
        max_y = int(self.df['anio'].max())
        
        self.ui_parameters.set_years(min_y, max_y)
        self.ui_simulation.set_years(min_y, max_y)
        self.ui_calibration.set_years(min_y, max_y)

    def calculate_linear_parameters(self, anio_ini, anio_fin):
        if self.df is None:
            raise ValueError("Primero cargue los datos.")
            
        delta, delta_s, delta_n = estimar_tasas_defuncion(self.df, anio_ini, anio_fin)
        m = estimar_m(self.df, anio_ini, anio_fin)
        
        # Valores iniciales por defecto para los no lineales
        theta = 0.1
        rho = 0.5
        beta = 0.5
        gamma = 1.0
        
        # Phi inicial
        phi = 0.5
        phi, psi = calcular_phi_psi(m, phi)
        
        self.params = ModeloParametros(
            delta=delta,
            delta_s=delta_s,
            delta_n=delta_n,
            m=m,
            phi=phi,
            psi=psi,
            theta=theta,
            rho=rho,
            beta=beta,
            gamma=gamma
        )

    def build_linear_series(self):
        if self.df is None or self.params is None:
            raise ValueError("Faltan datos o parámetros.")
            
        self.df = construir_series_lineales(
            self.df, 
            self.params.m, 
            self.params.phi, 
            self.params.psi
        )

    def update_nonlinear_params_from_ui(self):
        if self.params:
            ui_vals = self.ui_parameters.get_nonlinear_params()
            self.params.theta = ui_vals['theta']
            self.params.rho = ui_vals['rho']
            self.params.beta = ui_vals['beta']
            self.params.gamma = ui_vals['gamma']

    def run_simulation(self, anio_ini, anio_fin):
        if self.df is None or self.params is None:
            raise ValueError("Faltan datos o parámetros.")
            
        return prueba_escritorio(self.df, self.params, anio_ini, anio_fin)
