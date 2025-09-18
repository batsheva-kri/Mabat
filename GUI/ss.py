import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("מערכת מכירות")
        self.resize(300, 200)
        layout = QVBoxLayout()
        self.label = QLabel("התחברות למערכת")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("שם משתמש")
        self.user_input.setLayoutDirection(1)  # RTL
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("סיסמה")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setLayoutDirection(1)
        self.button = QPushButton("התחבר")
        self.button.clicked.connect(self.login)
        layout.addWidget(self.label)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.button)
        self.setLayout(layout)
    def login(self):
        QMessageBox.information(self, "ברוך הבא", f"שלום {self.user_input.text()}")
app = QApplication(sys.argv)
window = LoginWindow()
window.show()
sys.exit(app.exec_())