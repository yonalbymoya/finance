import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
import sys
from PyQt5.QtWidgets import QApplication
from views.login import LoginWindow
from views.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    if login_window.exec_() == LoginWindow.Accepted:
        main_window = MainWindow()  
        main_window.show()
    sys.exit(app.exec_())
