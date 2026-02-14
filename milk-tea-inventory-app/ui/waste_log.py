"""BrewMetric Waste Log Page - Track waste and spoilage."""

from datetime import datetime
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QComboBox,
    QSpinBox, QDoubleSpinBox, QMessageBox, QTextEdit,
    QDateEdit, QLineEdit
)
from PySide6.QtCore import Qt
from database import (
    User, DatabaseManager, WasteLog, InventoryItem,
    InventoryQueries, WasteQueries
)
from ui.styles import Styles
from config import WASTE_REASONS, COLORS


class WasteLogPage(QWidget):
    """Waste log tracking page."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.init_ui()
        self.load_waste_logs()
    
    def init_ui(self):
        """Initialize UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        title = QLabel("Waste Log")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        main_layout.addWidget(title)
        
        subtitle = QLabel("Track all waste, spoilage, and damaged items")
        subtitle.setObjectName("muted")
        main_layout.addWidget(subtitle)
        
        # Controls
        controls = QHBoxLayout()
        
        add_btn = QPushButton("➕ Record Waste")
        add_btn.clicked.connect(self.show_add_waste_dialog)
        controls.addWidget(add_btn)
        
        controls.addStretch()
        
        main_layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Item", "Quantity", "Unit", "Reason", "User", "Notes"
        ])
        self.table.setStyleSheet(Styles.get_global_stylesheet())
        self.table.setMinimumHeight(400)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def load_waste_logs(self):
        """Load recent waste logs."""
        try:
            logs = WasteQueries.get_recent_waste(self.session, limit=100)
            self.display_logs(logs)
        except Exception as e:
            print(f"[v0] Error loading waste logs: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load waste logs: {e}")
    
    def display_logs(self, logs: list):
        """Display waste logs in table."""
        self.table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(
                log.created_at.strftime("%Y-%m-%d %H:%M")
            ))
            self.table.setItem(row, 1, QTableWidgetItem(log.inventory_item.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{log.quantity:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(log.inventory_item.unit))
            self.table.setItem(row, 4, QTableWidgetItem(log.reason))
            self.table.setItem(row, 5, QTableWidgetItem(log.user.full_name))
            self.table.setItem(row, 6, QTableWidgetItem(log.notes or ""))
    
    def show_add_waste_dialog(self):
        """Show dialog to add waste entry."""
        dialog = WasteDialog(self, self.session)
        if dialog.exec():
            try:
                waste_log = WasteLog(
                    inventory_item_id=dialog.item_id,
                    user_id=self.user.id,
                    quantity=dialog.quantity,
                    reason=dialog.reason,
                    notes=dialog.notes
                )
                
                # Update inventory quantity
                item = self.session.query(InventoryItem).get(dialog.item_id)
                item.quantity = max(0, item.quantity - dialog.quantity)
                
                self.session.add(waste_log)
                self.session.commit()
                
                self.load_waste_logs()
                QMessageBox.information(self, "Success", "Waste entry recorded")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Failed to record waste: {e}")


class WasteDialog(QDialog):
    """Dialog for recording waste."""
    
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        self.setWindowTitle("Record Waste")
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet(Styles.get_global_stylesheet())
        self.session = session
        self.item_id = None
        self.quantity = 0
        self.reason = ""
        self.notes = ""
        self.init_ui()
    
    def init_ui(self):
        """Initialize form."""
        layout = QVBoxLayout()
        
        # Item selection
        layout.addWidget(QLabel("Select Item:"))
        self.item_combo = QComboBox()
        try:
            from database import InventoryQueries
            items = InventoryQueries.get_all_items(self.session)
            for item in items:
                self.item_combo.addItem(item.name, item.id)
        except:
            pass
        layout.addWidget(self.item_combo)
        
        # Quantity
        layout.addWidget(QLabel("Quantity:"))
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setValue(1)
        layout.addWidget(self.qty_input)
        
        # Reason
        layout.addWidget(QLabel("Reason:"))
        self.reason_combo = QComboBox()
        self.reason_combo.addItems(WASTE_REASONS)
        layout.addWidget(self.reason_combo)
        
        # Notes
        layout.addWidget(QLabel("Notes (Optional):"))
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(100)
        layout.addWidget(self.notes_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Record")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and accept."""
        if self.item_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation", "Select an item")
            return
        
        self.item_id = self.item_combo.currentData()
        self.quantity = self.qty_input.value()
        self.reason = self.reason_combo.currentText()
        self.notes = self.notes_input.toPlainText()
        
        super().accept()
