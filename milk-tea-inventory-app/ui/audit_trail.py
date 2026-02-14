"""BrewMetric Audit Trail Page - Admin-only access audit logs."""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QMessageBox, QPushButton
)
from database import User, DatabaseManager, AuditQueries
from ui.styles import Styles


class AuditTrailPage(QWidget):
    """Audit trail viewer page (admin-only)."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.init_ui()
        self.load_audit_logs()
    
    def init_ui(self):
        """Initialize UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        title = QLabel("Audit Trail (Admin Only)")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        main_layout.addWidget(title)
        
        subtitle = QLabel("Complete log of all system actions for compliance and security")
        subtitle.setObjectName("muted")
        main_layout.addWidget(subtitle)
        
        # Controls
        controls = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search actions...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_logs)
        controls.addWidget(self.search_input)
        
        self.action_filter = QComboBox()
        self.action_filter.addItems(["All Actions", "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE"])
        self.action_filter.setMaximumWidth(200)
        self.action_filter.currentTextChanged.connect(self.filter_logs)
        controls.addWidget(self.action_filter)
        
        controls.addStretch()
        
        export_btn = QPushButton("📥 Export CSV")
        export_btn.clicked.connect(self.export_audit_log)
        controls.addWidget(export_btn)
        
        main_layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "User", "Action", "Entity", "Entity ID",
            "Description", "Old Value", "New Value", "IP Address"
        ])
        self.table.setStyleSheet(Styles.get_global_stylesheet())
        self.table.setMinimumHeight(400)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def load_audit_logs(self):
        """Load audit logs."""
        try:
            logs = AuditQueries.get_recent_actions(self.session, limit=500)
            self.display_logs(logs)
        except Exception as e:
            print(f"[v0] Error loading audit logs: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {e}")
    
    def display_logs(self, logs: list):
        """Display audit logs in table."""
        self.table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(
                log.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.table.setItem(row, 1, QTableWidgetItem(log.user.username))
            self.table.setItem(row, 2, QTableWidgetItem(log.action))
            self.table.setItem(row, 3, QTableWidgetItem(log.entity_type))
            self.table.setItem(row, 4, QTableWidgetItem(str(log.entity_id)))
            self.table.setItem(row, 5, QTableWidgetItem(log.description or ""))
            self.table.setItem(row, 6, QTableWidgetItem(log.old_values or ""))
            self.table.setItem(row, 7, QTableWidgetItem(log.new_values or ""))
            self.table.setItem(row, 8, QTableWidgetItem(log.ip_address or "N/A"))
    
    def filter_logs(self):
        """Filter audit logs."""
        search_text = self.search_input.text().lower()
        action_filter = self.action_filter.currentText()
        
        try:
            logs = AuditQueries.get_recent_actions(self.session, limit=500)
            
            # Filter
            filtered = [
                log for log in logs
                if (search_text in log.description.lower() if log.description else False or
                    search_text in log.user.username.lower() or
                    search_text in log.action.lower()) and
                   (action_filter == "All Actions" or log.action == action_filter)
            ]
            
            self.display_logs(filtered)
        except Exception as e:
            print(f"[v0] Error filtering: {e}")
    
    def export_audit_log(self):
        """Export audit log to CSV."""
        try:
            from utils import ExcelExporter
            import os
            
            logs = AuditQueries.get_recent_actions(self.session, limit=5000)
            filepath = os.path.expanduser(f"~/Desktop/brewmetric_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            ExcelExporter.export_audit_trail_csv(logs, filepath)
            QMessageBox.information(self, "Success", f"Audit log exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")


from datetime import datetime
