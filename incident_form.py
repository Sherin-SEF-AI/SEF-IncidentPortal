from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QVBoxLayout, QGridLayout, QMessageBox, QTreeWidget, QTreeWidgetItem, QFileDialog)
from PyQt5.QtCore import QDateTime
from database import insert_incident, get_all_incidents, register_user, authenticate_user, get_incident_stats
from config import ADMIN_EMAIL, LOG_FILE
import logging
import smtplib
from email.mime.text import MIMEText
import hashlib

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IncidentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        layout.addWidget(QLabel("Incident Type:"), 0, 0)
        self.type_entry = QLineEdit(self)
        layout.addWidget(self.type_entry, 0, 1)

        layout.addWidget(QLabel("Description:"), 1, 0)
        self.description_entry = QTextEdit(self)
        layout.addWidget(self.description_entry, 1, 1)

        layout.addWidget(QLabel("Date/Time:"), 2, 0)
        self.datetime_entry = QLineEdit(self)
        self.datetime_entry.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm"))
        layout.addWidget(self.datetime_entry, 2, 1)

        layout.addWidget(QLabel("Severity:"), 3, 0)
        self.severity_var = QComboBox(self)
        self.severity_var.addItems(["Low", "Medium", "High", "Critical"])
        layout.addWidget(self.severity_var, 3, 1)

        layout.addWidget(QLabel("Status:"), 4, 0)
        self.status_var = QComboBox(self)
        self.status_var.addItems(["Open", "In Progress", "Resolved"])
        layout.addWidget(self.status_var, 4, 1)

        layout.addWidget(QLabel("File Attachment:"), 5, 0)
        self.attachment_entry = QLineEdit(self)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.attachment_entry, 5, 1)
        layout.addWidget(browse_button, 5, 2)

        layout.addWidget(QLabel("Username:"), 6, 0)
        self.username_entry = QLineEdit(self)
        layout.addWidget(self.username_entry, 6, 1)

        layout.addWidget(QLabel("Password:"), 7, 0)
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry, 7, 1)

        submit_button = QPushButton("Submit Report", self)
        submit_button.clicked.connect(self.submit_report)
        layout.addWidget(submit_button, 8, 0, 1, 2)

        self.setLayout(layout)

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*);;Image Files (*.png *.jpg *.jpeg *.bmp);;PDF Files (*.pdf)", options=options)
        if file_path:
            self.attachment_entry.setText(file_path)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self):
        username = self.username_entry.text()
        password = self.hash_password(self.password_entry.text())
        return authenticate_user(username, password)

    def send_email_notification(self, incident_data):
        subject = "New Incident Report Submitted"
        body = f"""
        A new incident report has been submitted:

        Type: {incident_data[0]}
        Description: {incident_data[1]}
        Date/Time: {incident_data[2]}
        Severity: {incident_data[3]}
        Status: {incident_data[4]}
        Reporter: {incident_data[5]}
        Attachment: {incident_data[6]}
        """
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL

        try:
            with smtplib.SMTP('smtp.example.com') as server:
                server.starttls()
                server.login(ADMIN_EMAIL, 'your_password')  # Replace with actual credentials
                server.send_message(msg)
            logging.info(f"Email notification sent to {ADMIN_EMAIL}")
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")

    def submit_report(self):
        if self.authenticate_user():
            incident_type = self.type_entry.text()
            description = self.description_entry.toPlainText().strip()
            date_time = self.datetime_entry.text()
            severity = self.severity_var.currentText()
            status = self.status_var.currentText()
            reporter = self.username_entry.text()
            attachment = self.attachment_entry.text()

            if not incident_type or not description or not date_time:
                QMessageBox.critical(self, "Input Error", "All fields except Status are required!")
                return

            incident_data = (incident_type, description, date_time, severity, status, reporter, attachment)

            try:
                insert_incident(incident_data)
                logging.info(f"Incident report submitted by {reporter}")
                self.send_email_notification(incident_data)
                QMessageBox.information(self, "Success", "Incident report submitted successfully!")
                self.clear_fields()
            except Exception as e:
                logging.error(f"Error submitting incident report: {e}")
                QMessageBox.critical(self, "Submission Error", "Failed to submit incident report.")
        else:
            QMessageBox.critical(self, "Authentication Error", "Authentication Failed!")

    def clear_fields(self):
        self.type_entry.clear()
        self.description_entry.clear()
        self.datetime_entry.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm"))
        self.username_entry.clear()
        self.password_entry.clear()
        self.attachment_entry.clear()

class IncidentList(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(8)
        self.tree.setHeaderLabels(["ID", "Type", "Description", "Date/Time", "Severity", "Status", "Reporter", "Attachment"])
        layout.addWidget(self.tree)

        refresh_button = QPushButton("Refresh", self)
        refresh_button.clicked.connect(self.load_incidents)
        layout.addWidget(refresh_button)

        self.setLayout(layout)
        self.load_incidents()

    def load_incidents(self):
        self.tree.clear()
        incidents = get_all_incidents()
        for incident in incidents:
            QTreeWidgetItem(self.tree, [str(field) for field in incident])

class RegistrationForm(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Username:"))
        self.username_entry = QLineEdit(self)
        layout.addWidget(self.username_entry)

        layout.addWidget(QLabel("Password:"))
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        register_button = QPushButton("Register", self)
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self):
        username = self.username_entry.text()
        password = self.hash_password(self.password_entry.text())

        try:
            register_user(username, password)
            QMessageBox.information(self, "Success", "User registered successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Registration Error", f"Failed to register user: {e}")

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Username:"))
        self.username_entry = QLineEdit(self)
        layout.addWidget(self.username_entry)

        layout.addWidget(QLabel("Password:"))
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.login_user)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_user(self):
        username = self.username_entry.text()
        password = self.hash_password(self.password_entry.text())

        if authenticate_user(username, password):
            QMessageBox.information(self, "Success", "Login successful!")
        else:
            QMessageBox.critical(self, "Login Error", "Invalid username or password!")

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.stats_label = QLabel("Incident Statistics will be displayed here.")
        layout.addWidget(self.stats_label)

        refresh_button = QPushButton("Refresh Statistics", self)
        refresh_button.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def refresh_stats(self):
        stats = get_incident_stats()
        self.stats_label.setText(f"Incident Statistics:\n\n{stats}")
