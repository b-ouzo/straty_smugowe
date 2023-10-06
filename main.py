from GUI import *
from model import Model
from controller import App
import sys
from PyQt6.QtWidgets import QApplication

# 2. Create an instance of QApplication
if __name__ == "__main__":
    if not QApplication.instance():
            app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = AppMainWindow()
    # window.workingIm.loadImage(
    #     r'.\examplary_pictures\SET_2_WG3.bmp'
    # )
    # window.workingIm.clearView()
    window.show()
    model = Model()
    App(model, window)
    window.resize(1201, int(1200*0.76)) # to rescale image properly
    sys.exit(app.exec())