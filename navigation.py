from screens.calculator import CalculatorScreen
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.catalog import CatalogScreen
from screens.employees import EmployeeManagementScreen
from screens.documents import DocumentsScreen

class Navigator:
    def __init__(self, page):
        self.page = page
        self.connected_users = []

    def go_home(self, user):
        if not any(u["id"] == user["id"] for u in self.connected_users):
            self.connected_users.append(user)
        HomeScreen(self.page, user, self)

    def go_login(self):
        LoginScreen(self.page, self)

    def go_catalog(self, user, mode="inventory"):
        CatalogScreen(self.page, self, user, mode)

    def go_employee_management(self, user):
        EmployeeManagementScreen(self.page, self, user)

    def go_calculator(self, user):
        CalculatorScreen(self.page, user, self)

    def go_documents(self, user):
        self.page.clean()
        DocumentsScreen(self.page, user, self)
