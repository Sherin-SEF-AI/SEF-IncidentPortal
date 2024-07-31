from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from incident_form import IncidentForm, IncidentList, RegistrationForm, LoginForm, Dashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Incident Reporting Portal")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.login_form = LoginForm()
        self.registration_form = RegistrationForm()
        self.dashboard = Dashboard()
        self.incident_form = IncidentForm()
        self.incident_list = IncidentList()

        self.tab_widget.addTab(self.login_form, "Login")
        self.tab_widget.addTab(self.registration_form, "Register")
        self.tab_widget.addTab(self.dashboard, "Dashboard")
        self.tab_widget.addTab(self.incident_form, "Submit Incident")
        self.tab_widget.addTab(self.incident_list, "View Incidents")

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
