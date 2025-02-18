import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QDialog
from PyQt5 import uic
from controllers.auth_controller import validation_login

class LoginWindow(QDialog):
    Accepted = 1
    Rejected = 0
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/login.ui", self)
        
        self.btn_login.clicked.connect(self.handle_login)

    def handle_login(self):
        self.accept()
        """username = self.input_user.text()
        password = self.input_pass.text()

        if validation_login(username, password):
            QMessageBox.information(self, "Éxito", "Login Exitoso")
            self.accept()
            
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña erroneo")"""


    """def open_main_window(self):
        from main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
