from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView)
import pandas as pd
from core.parameters import ModeloParametros
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

        # Sección de Tabla Comparativa
        table_group = QGroupBox("Tabla Comparativa: Observados vs Simulados")
        table_layout = QVBoxLayout()
        
        self.table_comparison = QTableWidget()
        self.table_comparison.setColumnCount(5)
        self.table_comparison.setHorizontalHeaderLabels(["Año", "T_obs", "T_model", "Error Abs", "Error Rel (%)"])
        self.table_comparison.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.table_comparison)
        
        table_group.setLayout(table_layout)
        self.layout.addWidget(table_group)
        
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
            # Primero calculamos estadísticas para obtener el res_df actualizado
            stats = calculate_statistics(self.main_window.df, self.main_window.params, anio_ini, anio_fin)
            res_df = stats.get('res_df', None)
            
            if res_df is not None:
                self.actualizar_desde_resultados(res_df, self.main_window.params, anio_ini, anio_fin)
            else:
                QMessageBox.warning(self, "Error", "No se pudieron generar los datos simulados.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular estadísticas: {e}")

    def actualizar_tabla_comparativa(self, df_resultados: pd.DataFrame) -> None:
        """
        Llena la tabla de la pestaña Conclusiones con las columnas:
        anio, T_obs, T_model, error_abs, error_rel (%).
        """
        if df_resultados is None or df_resultados.empty:
            self.table_comparison.setRowCount(0)
            return

        # Filtrar filas donde existan tanto T_obs como T_model (o al menos T_model para mostrar)
        # Para la comparativa, idealmente necesitamos ambos, pero mostraremos lo que haya.
        # Asumimos que df_resultados tiene 'anio', 'T_obs', 'T_model'
        
        # Crear copia para no modificar el original
        df = df_resultados.copy()
        
        # Calcular errores si no existen
        if 'error' not in df.columns:
            df['error'] = df['T_model'] - df['T_obs']
        if 'error_rel' not in df.columns:
            df['error_rel'] = (df['error'] / df['T_obs']).abs() * 100
            
        # Seleccionar columnas de interés
        cols = ['anio', 'T_obs', 'T_model', 'error', 'error_rel']
        
        # Limpiar tabla
        self.table_comparison.setRowCount(0)
        
        # Llenar tabla
        for _, row in df.iterrows():
            row_idx = self.table_comparison.rowCount()
            self.table_comparison.insertRow(row_idx)
            
            # Año
            self.table_comparison.setItem(row_idx, 0, QTableWidgetItem(str(int(row['anio']))))
            
            # T_obs
            val_obs = row['T_obs']
            str_obs = f"{val_obs:.1f}" if pd.notnull(val_obs) else "-"
            self.table_comparison.setItem(row_idx, 1, QTableWidgetItem(str_obs))
            
            # T_model
            val_model = row['T_model']
            str_model = f"{val_model:.0f}" if pd.notnull(val_model) else "-"
            self.table_comparison.setItem(row_idx, 2, QTableWidgetItem(str_model))
            
            # Error Abs
            val_err = abs(row['error'])
            str_err = f"{val_err:.1f}" if pd.notnull(val_err) else "-"
            self.table_comparison.setItem(row_idx, 3, QTableWidgetItem(str_err))
            
            # Error Rel
            val_rel = row['error_rel']
            str_rel = f"{val_rel:.2f}%" if pd.notnull(val_rel) else "-"
            self.table_comparison.setItem(row_idx, 4, QTableWidgetItem(str_rel))

    def actualizar_desde_resultados(
        self,
        df_resultados: pd.DataFrame,
        params_actuales: ModeloParametros,
        anio_ini: int,
        anio_fin: int
    ) -> None:
        """
        - Actualiza la tabla comparativa con df_resultados.
        - Recalcula las estadísticas de ajuste.
        - Genera el texto de conclusiones generales.
        - Genera el párrafo específico sobre la tabla comparativa.
        - Muestra todo en la pestaña Conclusiones.
        """
        # 1. Actualizar tabla
        self.actualizar_tabla_comparativa(df_resultados)
        
        # 2. Calcular estadísticas
        # Nota: calculate_statistics recalcula la simulación internamente si se le pasa solo df y params.
        # Pero aquí ya tenemos df_resultados (que se supone es el resultado de la simulación).
        # Sin embargo, calculate_statistics está diseñado para recibir el df de entrada (observados) y params.
        # Para evitar doble cálculo, podríamos refactorizar calculate_statistics, pero por ahora lo usaremos como está
        # asumiendo que es rápido o que df_resultados es consistente.
        # O mejor, usamos calculate_statistics para obtener las métricas y le pasamos el df_resultados si fuera posible.
        # Dado que calculate_statistics llama a prueba_escritorio, y eso es rápido, lo llamamos normal.
        
        try:
            stats = calculate_statistics(self.main_window.df, params_actuales, anio_ini, anio_fin)
            
            self.lbl_r2.setText(f"{stats['R2']:.4f}")
            self.lbl_mse.setText(f"{stats['MSE']:.4f}")
            self.lbl_rmse.setText(f"{stats['RMSE']:.4f}")
            self.lbl_mae.setText(f"{stats['MAE']:.4f}")
            self.lbl_mape.setText(f"{stats['MAPE']:.2f}%")
            
            # 3. Generar texto
            # Usamos el res_df que devuelve stats, que debería ser igual a df_resultados si los params son los mismos
            res_df = stats.get('res_df', df_resultados)
            
            text = generar_texto_conclusion_detallada(stats, params_actuales, res_df, anio_ini, anio_fin)
            self.text_conclusions.setPlainText(text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar conclusiones: {e}")
            
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
