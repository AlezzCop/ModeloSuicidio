from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Traducir acciones de la barra de herramientas
        for action in self.toolbar.actions():
            if action.text() == 'Home':
                action.setText('Inicio')
                action.setToolTip('Restablecer vista original')
            elif action.text() == 'Back':
                action.setText('Atrás')
                action.setToolTip('Vista anterior')
            elif action.text() == 'Forward':
                action.setText('Adelante')
                action.setToolTip('Vista siguiente')
            elif action.text() == 'Pan':
                action.setText('Mover')
                action.setToolTip('Mover el gráfico')
            elif action.text() == 'Zoom':
                action.setText('Zoom')
                action.setToolTip('Acercar/Alejar')
            elif action.text() == 'Subplots':
                action.setText('Subtramas')
                action.setToolTip('Configurar subtramas')
            elif action.text() == 'Customize':
                action.setText('Personalizar')
                action.setToolTip('Editar parámetros del gráfico')
            elif action.text() == 'Save':
                action.setText('Guardar')
                action.setToolTip('Guardar la figura')
        
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        
        # Etiqueta para descripción de la gráfica
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt
        self.lbl_description = QLabel("")
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl_description.setStyleSheet("font-size: 11px; color: #333; padding: 5px; background-color: #f0f0f0; border-radius: 4px;")
        self.lbl_description.hide() # Ocultar por defecto si no hay texto
        
        self.layout.addWidget(self.lbl_description)
        
    def get_figure(self):
        return self.figure
        
    def draw(self):
        self.canvas.draw()
        
    def set_description(self, text):
        if text:
            self.lbl_description.setText(text)
            self.lbl_description.show()
        else:
            self.lbl_description.clear()
            self.lbl_description.hide()
