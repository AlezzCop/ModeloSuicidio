from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QMessageBox, QProgressBar, QPlainTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal
from .matplotlib_widget import MatplotlibWidget

class CalibrationWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object, float, str)
    error = pyqtSignal(str)

    def __init__(self, main_window, anio_ini, anio_fin, num_theta, num_gamma):
        super().__init__()
        self.main_window = main_window
        self.anio_ini = anio_ini
        self.anio_fin = anio_fin
        self.num_theta = num_theta
        self.num_gamma = num_gamma

    def run(self):
        try:
            from core.calibration import calibrar_parametros
            
            def cb(p):
                self.progress.emit(p)

            params, cost, log = calibrar_parametros(
                self.main_window.df,
                self.main_window.params,
                self.anio_ini,
                self.anio_fin,
                self.num_theta,
                self.num_gamma,
                progress_callback=cb
            )
            self.finished.emit(params, cost, log)
        except Exception as e:
            self.error.emit(str(e))

class CalibrationView(QWidget):
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
        
        self.spin_mesh = QSpinBox()
        self.spin_mesh.setRange(2, 50)
        self.spin_mesh.setValue(10)
        
        self.btn_calib = QPushButton("Iniciar Calibración")
        self.btn_calib.clicked.connect(self.start_calibration)
        
        controls_layout.addWidget(QLabel("Año Inicio:"))
        controls_layout.addWidget(self.spin_start)
        controls_layout.addWidget(QLabel("Año Fin:"))
        controls_layout.addWidget(self.spin_end)
        lbl_mesh = QLabel("Malla (NxN):")
        lbl_mesh.setToolTip("Este parámetro no se utiliza en el método de optimización actual (least_squares).")
        self.spin_mesh.setToolTip("Este parámetro no se utiliza en el método de optimización actual (least_squares).")
        controls_layout.addWidget(lbl_mesh)
        controls_layout.addWidget(self.spin_mesh)
        controls_layout.addWidget(self.btn_calib)
        controls_layout.addStretch()
        
        self.layout.addLayout(controls_layout)
        
        # Progreso y Log
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)
        
    def set_years(self, min_y, max_y):
        self.spin_start.setValue(min_y)
        self.spin_end.setValue(max_y)

    def start_calibration(self):
        self.btn_calib.setEnabled(False)
        self.log_text.clear()
        self.log_text.appendPlainText("Iniciando calibración...")
        
        self.worker = CalibrationWorker(
            self.main_window,
            self.spin_start.value(),
            self.spin_end.value(),
            self.spin_mesh.value(),
            self.spin_mesh.value()
        )
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, params, cost, log):
        self.btn_calib.setEnabled(True)
        self.progress_bar.setValue(100)
        self.log_text.appendPlainText(log)
        self.log_text.appendPlainText(f"\nCalibración finalizada.\nCosto final: {cost:.4f}")
        self.log_text.appendPlainText(f"Parámetros calibrados:\nTheta: {params.theta}\nRho: {params.rho}\nBeta: {params.beta}\nGamma: {params.gamma}")
        
        # Actualizar modelo principal
        self.main_window.params = params
        self.main_window.ui_parameters.update_display_params()
        
        QMessageBox.information(self, "Éxito", "Calibración completada. Parámetros actualizados.")

    def on_error(self, msg):
        self.btn_calib.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)
