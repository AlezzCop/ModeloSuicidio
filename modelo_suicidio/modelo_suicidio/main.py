import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Intentar cargar Simulacion.xlsx si existe
    default_file = os.path.join(os.path.dirname(__file__), "Simulacion.xlsx")
    if os.path.exists(default_file):
        try:
            window.load_data(default_file)
            window.ui_data.update_view()
            print(f"Datos cargados automáticamente de {default_file}")
        except Exception as e:
            print(f"No se pudo cargar el archivo por defecto: {e}")
            
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
