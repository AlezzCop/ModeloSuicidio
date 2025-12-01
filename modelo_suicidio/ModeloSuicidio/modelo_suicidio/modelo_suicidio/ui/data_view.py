from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFileDialog, QTableView, QLabel, QHeaderView, QMessageBox)
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
from .matplotlib_widget import MatplotlibWidget

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None

class DataView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        
        # Controles superiores
        top_layout = QHBoxLayout()
        self.btn_load = QPushButton("Cargar Excel")
        self.btn_load.clicked.connect(self.load_excel)
        self.lbl_info = QLabel("No se han cargado datos.")
        
        top_layout.addWidget(self.btn_load)
        top_layout.addWidget(self.lbl_info)
        top_layout.addStretch()
        
        self.layout.addLayout(top_layout)
        
        # Tabla
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)
        
        # Gráficos
        self.plot_widget = MatplotlibWidget()
        self.layout.addWidget(self.plot_widget)
        
    def load_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Excel", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            try:
                self.main_window.load_data(file_name)
                self.update_view()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def update_view(self):
        df = self.main_window.df
        if df is not None:
            # Actualizar tabla
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            # Actualizar info
            min_year = df['anio'].min()
            max_year = df['anio'].max()
            self.lbl_info.setText(f"Datos cargados: {min_year} - {max_year} ({len(df)} registros)")
            
            # Actualizar gráficos
            fig = self.plot_widget.get_figure()
            fig.clear()
            
            ax1 = fig.add_subplot(121)
            ax1.plot(df['anio'], df['Poblacion_10ymas_P'], 'b-o')
            ax1.set_title("Población Vulnerable P(t)")
            ax1.set_xlabel("Año")
            ax1.grid(True)
            
            ax2 = fig.add_subplot(122)
            ax2.plot(df['anio'], df['T_obs'], 'r-o')
            ax2.set_title("Tratamiento Observado T_obs(t)")
            ax2.set_xlabel("Año")
            ax2.grid(True)
            
            self.plot_widget.draw()
            
            # Agregar descripción
            desc = "<b>Gráfica de Población Vulnerable P(t):</b><br>"
            desc += "Esta gráfica muestra la evolución de la población vulnerable a lo largo del tiempo, representada por la serie de datos de P(t). Los puntos representan los valores reales de la población cada año.<br><br>"
            desc += "<b>Gráfica de Tratamiento Observado T_obs(t):</b><br>"
            desc += "En esta gráfica, los puntos rojos representan los casos observados en tratamiento (T_obs) cada año."
            
            self.plot_widget.set_description(desc)
