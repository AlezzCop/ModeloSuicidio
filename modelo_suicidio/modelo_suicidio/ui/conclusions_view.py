from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QGroupBox, QFormLayout, QMessageBox, QFileDialog)
from core.statistics import calculate_statistics, generar_texto_conclusion_detallada

class ConclusionsView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        
        # Sección de Estadísticas
        stats_group = QGroupBox("Estadísticas de Ajuste")
        stats_layout = QFormLayout()
        
        self.lbl_r2 = QLabel("-")
        self.lbl_mse = QLabel("-")
        self.lbl_rmse = QLabel("-")
        self.lbl_mae = QLabel("-")
        self.lbl_mape = QLabel("-")
        
        stats_layout.addRow("R² (Coeficiente de Determinación):", self.lbl_r2)
        stats_layout.addRow("MSE (Error Cuadrático Medio):", self.lbl_mse)
        stats_layout.addRow("RMSE (Raíz del Error Cuadrático Medio):", self.lbl_rmse)
        stats_layout.addRow("MAE (Error Absoluto Medio):", self.lbl_mae)
        stats_layout.addRow("MAPE (Error Porcentual Absoluto Medio):", self.lbl_mape)
        
        stats_group.setLayout(stats_layout)
        self.layout.addWidget(stats_group)
        
        # Sección de Conclusiones
        concl_group = QGroupBox("Conclusiones Automáticas")
        concl_layout = QVBoxLayout()
        
        self.text_conclusions = QTextEdit()
        self.text_conclusions.setReadOnly(False) # Permitir edición si el usuario quiere ajustar
        concl_layout.addWidget(self.text_conclusions)
        
        concl_group.setLayout(concl_layout)
        self.layout.addWidget(concl_group)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.btn_update = QPushButton("Actualizar Conclusiones")
        self.btn_update.clicked.connect(self.update_view)
        
        self.btn_export = QPushButton("Exportar Informe")
        self.btn_export.clicked.connect(self.export_report)
        
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_export)
        
        self.layout.addLayout(btn_layout)
        
    def update_view(self):
        if self.main_window.df is None or self.main_window.params is None:
            QMessageBox.warning(self, "Aviso", "Primero cargue datos y defina parámetros.")
            return
            
        # Usar el rango de años definido en la pestaña de simulación o calibración
        # Por defecto usaremos todo el rango de datos disponible
        anio_ini = int(self.main_window.df['anio'].min())
        anio_fin = int(self.main_window.df['anio'].max())
        
        try:
            stats = calculate_statistics(self.main_window.df, self.main_window.params, anio_ini, anio_fin)
            
            self.lbl_r2.setText(f"{stats['R2']:.4f}")
            self.lbl_mse.setText(f"{stats['MSE']:.4f}")
            self.lbl_rmse.setText(f"{stats['RMSE']:.4f}")
            self.lbl_mae.setText(f"{stats['MAE']:.4f}")
            self.lbl_mape.setText(f"{stats['MAPE']:.2f}%")
            
            # Recuperar el DataFrame de resultados de stats (agregado en calculate_statistics)
            res_df = stats.get('res_df', None)
            
            if res_df is not None:
                text = generar_texto_conclusion_detallada(stats, self.main_window.params, res_df, anio_ini, anio_fin)
                self.text_conclusions.setPlainText(text)
            else:
                self.text_conclusions.setPlainText("Error: No se pudieron generar los datos simulados para las conclusiones.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular estadísticas: {e}")
            
    def export_report(self):
        text = self.text_conclusions.toPlainText()
        if not text:
            QMessageBox.warning(self, "Aviso", "No hay conclusiones para exportar.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Informe", "Informe_Conclusiones.txt", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Éxito", f"Informe guardado en {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {e}")
