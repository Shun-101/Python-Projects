"""BrewMetric Inventory Page - CRUD interface for inventory items."""

from datetime import datetime, timedelta
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QDialog, QMessageBox,
    QDateEdit, QTextEdit
)
from database import (
    User, DatabaseManager, InventoryItem, InventoryQueries, ROLE_ADMIN
)
from ui.styles import Styles
from config import COLORS, STOCK_CATEGORIES


class InventoryPage(QWidget):
    """Inventory management page with full CRUD."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        """Initialize UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = QVBoxLayout()
        title = QLabel("Inventory Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(title)
        
        subtitle = QLabel("View and manage all inventory items")
        subtitle.setObjectName("muted")
        header.addWidget(subtitle)
        main_layout.addLayout(header)
        
        # Controls
        controls = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_inventory)
        controls.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        for cat in STOCK_CATEGORIES:
            self.category_filter.addItem(cat)
        self.category_filter.setMaximumWidth(200)
        self.category_filter.currentTextChanged.connect(self.filter_inventory)
        controls.addWidget(self.category_filter)
        
        controls.addStretch()
        
        add_btn = QPushButton("➕ Add Item")
        add_btn.clicked.connect(self.show_add_dialog)
        controls.addWidget(add_btn)
        
        main_layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Name", "Category", "Stock", "Min", "Unit Cost",
            "Total Value", "Expires", "Status"
        ])
        self.table.setStyleSheet(Styles.get_global_stylesheet())
        self.table.setMinimumHeight(400)
        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def load_inventory(self):
        """Load inventory items into table."""
        try:
            items = InventoryQueries.get_all_items(self.session)
            self.display_items(items)
        except Exception as e:
            print(f"[v0] Error loading inventory: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {e}")
    
    def display_items(self, items: list):
        """Display items in table."""
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.name))
            self.table.setItem(row, 1, QTableWidgetItem(item.category))
            
            qty_item = QTableWidgetItem(f"{item.quantity:.2f}")
            qty_item.setData(Qt.UserRole, item.id)
            self.table.setItem(row, 2, qty_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(f"{item.min_threshold:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${item.unit_cost:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${item.get_stock_value():.2f}"))
            
            exp_text = item.expiration_date.strftime("%Y-%m-%d") if item.expiration_date else "N/A"
            self.table.setItem(row, 6, QTableWidgetItem(exp_text))
            
            # Status
            if item.is_expired():
                status = "EXPIRED"
                color = COLORS['warning_red']
            elif item.is_expiring_soon():
                status = "EXPIRING"
                color = COLORS['caution_orange']
            elif item.is_below_threshold():
                status = "LOW"
                color = COLORS['warning_red']
            else:
                status = "OK"
                color = COLORS['accent_green']
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor(color))
            self.table.setItem(row, 7, status_item)
    
    def filter_inventory(self):
        """Filter inventory based on search and category."""
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        try:
            items = InventoryQueries.get_all_items(self.session)
            
            # Filter
            filtered = [
                item for item in items
                if (search_text in item.name.lower() or not search_text) and
                   (category == "All Categories" or item.category == category)
            ]
            
            self.display_items(filtered)
        except Exception as e:
            print(f"[v0] Error filtering: {e}")
    
    def show_add_dialog(self):
        """Show add item dialog."""
        if not self.user.role == ROLE_ADMIN:
            QMessageBox.warning(self, "Permission Denied", "Only admins can add items")
            return
        
        dialog = AddItemDialog(self)
        if dialog.exec():
            try:
                new_item = InventoryItem(
                    name=dialog.name,
                    category=dialog.category,
                    quantity=dialog.quantity,
                    unit=dialog.unit,
                    min_threshold=dialog.threshold,
                    unit_cost=dialog.cost,
                    expiration_date=dialog.expiration_date,
                    location=dialog.location
                )
                self.session.add(new_item)
                self.session.commit()
                self.load_inventory()
                QMessageBox.information(self, "Success", f"Item '{dialog.name}' added")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Failed to add item: {e}")
    
    def on_item_double_click(self, item):
        """Handle item double-click for editing."""
        if self.table.currentRow() < 0:
            return
        
        row = self.table.currentRow()
        item_id = self.table.item(row, 2).data(Qt.UserRole)
        
        try:
            item = self.session.query(InventoryItem).get(item_id)
            if item:
                dialog = EditItemDialog(self, item)
                if dialog.exec():
                    item.name = dialog.name
                    item.category = dialog.category
                    item.quantity = dialog.quantity
                    item.min_threshold = dialog.threshold
                    item.unit_cost = dialog.cost
                    self.session.commit()
                    self.load_inventory()
                    QMessageBox.information(self, "Success", "Item updated")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update item: {e}")


class AddItemDialog(QDialog):
    """Dialog for adding a new inventory item."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Inventory Item")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet(Styles.get_global_stylesheet())
        self.name = ""
        self.category = ""
        self.quantity = 0
        self.unit = "unit"
        self.threshold = 10
        self.cost = 0
        self.expiration_date = None
        self.location = ""
        self.init_ui()
    
    def init_ui(self):
        """Initialize form."""
        layout = QVBoxLayout()
        
        # Name
        layout.addWidget(QLabel("Item Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_input = QComboBox()
        self.category_input.addItems(STOCK_CATEGORIES)
        layout.addWidget(self.category_input)
        
        # Quantity
        layout.addWidget(QLabel("Initial Quantity:"))
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setValue(0)
        layout.addWidget(self.qty_input)
        
        # Unit
        layout.addWidget(QLabel("Unit:"))
        self.unit_input = QLineEdit()
        self.unit_input.setText("unit")
        layout.addWidget(self.unit_input)
        
        # Min Threshold
        layout.addWidget(QLabel("Minimum Threshold:"))
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setValue(10)
        layout.addWidget(self.threshold_input)
        
        # Cost
        layout.addWidget(QLabel("Unit Cost:"))
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setValue(0)
        layout.addWidget(self.cost_input)
        
        # Expiration
        layout.addWidget(QLabel("Expiration Date (Optional):"))
        self.exp_input = QDateEdit()
        self.exp_input.setDate(datetime.now().date() + timedelta(days=30))
        layout.addWidget(self.exp_input)
        
        # Location
        layout.addWidget(QLabel("Storage Location:"))
        self.location_input = QLineEdit()
        layout.addWidget(self.location_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate and accept."""
        if not self.name_input.text():
            QMessageBox.warning(self, "Validation", "Item name is required")
            return
        
        self.name = self.name_input.text()
        self.category = self.category_input.currentText()
        self.quantity = self.qty_input.value()
        self.unit = self.unit_input.text() or "unit"
        self.threshold = self.threshold_input.value()
        self.cost = self.cost_input.value()
        self.location = self.location_input.text()
        self.expiration_date = self.exp_input.date().toPython()
        
        super().accept()


class EditItemDialog(AddItemDialog):
    """Dialog for editing inventory item."""
    
    def __init__(self, parent=None, item=None):
        self.item = item
        super().__init__(parent)
        self.setWindowTitle(f"Edit {item.name}")
        
        if item:
            self.name_input.setText(item.name)
            self.category_input.setCurrentText(item.category)
            self.qty_input.setValue(item.quantity)
            self.unit_input.setText(item.unit)
            self.threshold_input.setValue(item.min_threshold)
            self.cost_input.setValue(item.unit_cost)
            self.location_input.setText(item.location or "")
