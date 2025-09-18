from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QPropertyAnimation
import sys
from PySide6 import QtWidgets, QtCore

class AnimatedSidebarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ניהול לקוחות - Sidebar עם אנימציה")
        self.setGeometry(200, 100, 1100, 600)

        self.sidebar_expanded = True

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #bbb;
                border-radius: 8px;
                padding: 6px;
                background-color: white;
            }
            QPushButton {
                background-color: #00b894;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #019875;
            }
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #0984e3;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)

        main_layout = QHBoxLayout(self)

        # יצירת תפריט צד
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setStyleSheet("background-color: #2d3436;")
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)

        # כפתור פתיחה/סגירה
        toggle_btn = QPushButton("≡")
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #636e72;
            }
        """)
        toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(toggle_btn)

        # כפתורי תפריט
        btn_customers = QPushButton("  לקוחות")
        btn_orders = QPushButton("  הזמנות")
        btn_settings = QPushButton("  הגדרות")

        for btn in [btn_customers, btn_orders, btn_settings]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: white;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #636e72;
                    border-radius: 6px;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        # אזור תוכן
        content_layout = QVBoxLayout()
        title = QLabel("📋 מערכת ניהול לקוחות")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: #2d3436; margin-bottom: 10px;")
        content_layout.addWidget(title)

        # אזור חיפוש
        search_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("הכנס שם לקוח")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("הכנס טלפון")
        search_btn = QPushButton(" חפש")
        search_btn.clicked.connect(self.search_customers)

        search_layout.addWidget(QLabel("שם:"))
        search_layout.addWidget(self.name_input)
        search_layout.addWidget(QLabel("טלפון:"))
        search_layout.addWidget(self.phone_input)
        search_layout.addWidget(search_btn)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["שם לקוח", "טלפון"])
        self.table.cellDoubleClicked.connect(self.show_orders)

        self.orders_frame = QFrame()
        self.orders_layout = QVBoxLayout()
        self.orders_frame.setLayout(self.orders_layout)

        content_layout.addLayout(search_layout)
        content_layout.addWidget(self.table)
        content_layout.addWidget(QLabel("הזמנות ללקוח נבחר:"))
        content_layout.addWidget(self.orders_frame)

        main_layout.addWidget(self.sidebar_frame)
        main_layout.addLayout(content_layout)

    def toggle_sidebar(self):
        animation = QPropertyAnimation(self.sidebar_frame, b"minimumWidth")
        animation.setDuration(300)
        if self.sidebar_expanded:
            animation.setStartValue(200)
            animation.setEndValue(50)
            self.sidebar_expanded = False
        else:
            animation.setStartValue(50)
            animation.setEndValue(200)
            self.sidebar_expanded = True
        animation.start()

    def search_customers(self):
        data = [
            {"id": 1, "name": "משה כהן", "phone": "050-1234567"},
            {"id": 2, "name": "שרה לוי", "phone": "052-7654321"}
        ]
        self.table.setRowCount(0)
        for customer in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(customer["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(customer["phone"]))

    def show_orders(self, row, column):
        orders = [
            {"date": "2025-08-14", "product": "שמלה", "size": "M", "qty": 2, "price": 300},
            {"date": "2025-07-20", "product": "חולצה", "size": "L", "qty": 1, "price": 120}
        ]
        for i in reversed(range(self.orders_layout.count())):
            self.orders_layout.itemAt(i).widget().deleteLater()
        for order in orders:
            lbl = QLabel(f"{order['date']} | {order['product']} | מידה: {order['size']} | כמות: {order['qty']} | מחיר: {order['price']}₪")
            lbl.setStyleSheet("background: white; padding: 5px; border-radius: 6px; margin: 3px 0;")
            self.orders_layout.addWidget(lbl)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(QtCore.Qt.RightToLeft)
    window = AnimatedSidebarApp()
    window.show()
    sys.exit(app.exec())
