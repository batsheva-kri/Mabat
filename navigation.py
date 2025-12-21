from screens.Invitation_supply import Invitation_supply
from screens.calculator import CalculatorScreen
from screens.customers import ExistingCustomerScreen
from screens.documents import DocumentsScreen
from screens.deliveries import DeliveriesScreen
from screens.employees import EmployeeManagementScreen
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.mainInventory import MainInvitationScreen
from screens.inventory import InventoryScreen
from screens.new_customer_page import NewCustomerPage
from screens.new_invitation_page import NewInvitationPage
from screens.show_customers import CustomersScreen
from screens.supplier_catalog import SupplierCatalogScreen
from screens.supplier_orders import OrdersScreen
from screens.supplier_reports import SupplierReportsScreen
from screens.suppliers import SuppliersScreen
from screens.catalog import CatalogScreen
from screens.suppliers_forms import EditSupplierScreen, DeleteSupplierScreen, AddSupplierScreen
from screens.yearlyReport import YearlyReportScreen


from screens.debts import DebtsScreen

from screens.suppliers_forms import EditSupplierScreen, DeleteSupplierScreen, AddSupplierScreen



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
    def go_debts(self, user):
        DebtsScreen(self.page, self, user)
    def go_supplier_orders(self,user):
        OrdersScreen(self.page,self,user)
    def go_add_supplier(self,user,on_save):
        AddSupplierScreen(self.page, self,user, on_save)
    def go_edit_suppliers(self,user,supplier_data,on_save):
        EditSupplierScreen(self.page, self, user,supplier_data,on_save)
    def go_delete_suppliers(self,user, supplier_data, on_save):
        DeleteSupplierScreen(self.page, self, user, supplier_data, on_save)
    def go_supplier_report(self,user):
        SupplierReportsScreen(self.page, user,self)
    def do_supplier_catalog(self,user):
        SupplierCatalogScreen(self.page,user,self)
    def go_inventory_screen(self, user,save_fn,show_dropdown = False):
        InventoryScreen(self.page, user, self, save_fn,show_dropdown)
    def go_yearly_report(self, user):
        YearlyReportScreen(self.page, user, self)
    def go_customers_screen(self, user):
        CustomersScreen(self.page, self, user)

