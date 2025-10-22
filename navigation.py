from screens.Invitation_supply import Invitation_supply
from screens.calculator import CalculatorScreen
from screens.customers import ExistingCustomerScreen
from screens.documents import DocumentsScreen
from screens.deliveries import DeliveriesScreen
from screens.employees import EmployeeManagementScreen
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.mainInventory import MainInvitationScreen
from screens.mune import InventoryMenuScreen
from screens.new_customer_page import NewCustomerPage
from screens.new_invitation_page import NewInvitationPage
from screens.suppliers import SuppliersScreen
from screens.catalog import CatalogScreen

class Navigator:
    def __init__(self, page):
        self.page = page
        self.connected_users = []

    def go_home(self, user):
        # הוספת המשתמש לרשימת מחוברים אם לא קיים
        if not any(u["id"] == user["id"] for u in self.connected_users):
            self.connected_users.append(user)
        HomeScreen(self.page, user, self)

    def go_login(self):
        LoginScreen(self.page, self)

    def go_suppliers(self,user):
        SuppliersScreen(self.page, user,self)
    def go_orders(self,user,e=None):
        MainInvitationScreen(self.page, self, current_user=user)
    def go_inventory(self,user,save_arrived,save_existing):
        InventoryMenuScreen(self.page,user,self,save_arrived,save_existing)
    def go_new_customer(self,user):
        NewCustomerPage(self.page, user, self)
    def go_customer(self,user):
        ExistingCustomerScreen(self.page, user, self)
    def go_employee_management(self, user):
        EmployeeManagementScreen(self.page, self, user)
    def go_calculator(self, user):
        CalculatorScreen(self.page, user, self)
    def go_documents(self, user):
        self.page.clean()
        DocumentsScreen(self.page, user, self)
    def go_catalog(self, user, mode="inventory"):
        CatalogScreen(self.page, self, user, mode)
    def go_deliveries(self, user):
        DeliveriesScreen(self.page, self, user)
    def go_new_invitation(self,user, c_id,is_new_invitation = False, existing_invitation = None, edit = True):
        NewInvitationPage(self, self.page, user,c_id,is_new_invitation, edit, existing_invitation)
    def go_invitations_supply(self,user):
        Invitation_supply(self, self.page, user)
