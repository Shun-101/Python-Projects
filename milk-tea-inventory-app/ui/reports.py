"""BrewMetric Reports Page - Export and analytics reports."""

import os
from datetime import datetime
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QDateEdit
)
from database import User, DatabaseManager, InventoryQueries, WasteQueries
from utils import ExcelExporter
from config import COLORS, ROLE_ADMIN


class ReportsPage(QWidget):
    """Reports and export page."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        title = QLabel("Reports & Export")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        main_layout.addWidget(title)
        
        subtitle = QLabel("Export inventory data, waste logs, and generate reports")
        subtitle.setObjectName("muted")
        main_layout.addWidget(subtitle)
        
        # Inventory Reports
        inv_section = self.create_section("📦 Inventory Reports")
        inv_layout = QVBoxLayout()
        
        inv_csv_btn = QPushButton("Export Inventory (CSV)")
        inv_csv_btn.setMinimumHeight(40)
        inv_csv_btn.clicked.connect(lambda: self.export_inventory("csv"))
        inv_layout.addWidget(inv_csv_btn)
        
        inv_excel_btn = QPushButton("Export Inventory (Excel)")
        inv_excel_btn.setMinimumHeight(40)
        inv_excel_btn.clicked.connect(lambda: self.export_inventory("excel"))
        inv_layout.addWidget(inv_excel_btn)
        
        inv_section.setLayout(inv_layout)
        main_layout.addWidget(inv_section)
        
        # Waste Reports
        waste_section = self.create_section("🗑️ Waste Log Reports")
        waste_layout = QVBoxLayout()
        
        waste_csv_btn = QPushButton("Export Waste Log (CSV)")
        waste_csv_btn.setMinimumHeight(40)
        waste_csv_btn.clicked.connect(lambda: self.export_waste("csv"))
        waste_layout.addWidget(waste_csv_btn)
        
        waste_excel_btn = QPushButton("Export Waste Log (Excel)")
        waste_excel_btn.setMinimumHeight(40)
        waste_excel_btn.clicked.connect(lambda: self.export_waste("excel"))
        waste_layout.addWidget(waste_excel_btn)
        
        waste_section.setLayout(waste_layout)
        main_layout.addWidget(waste_section)
        
        # Admin Reports
        if self.user.role == ROLE_ADMIN:
            admin_section = self.create_section("🔐 Admin Reports")
            admin_layout = QVBoxLayout()
            
            valuation_btn = QPushButton("Inventory Valuation Report")
            valuation_btn.setMinimumHeight(40)
            valuation_btn.clicked.connect(self.generate_valuation_report)
            admin_layout.addWidget(valuation_btn)
            
            admin_section.setLayout(admin_layout)
            main_layout.addWidget(admin_section)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def create_section(self, title: str) -> QFrame:
        """Create a report section frame."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary_bg']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        section_layout = QVBoxLayout()
        section_title = QLabel(title)
        section_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        section_layout.addWidget(section_title)
        
        # Will be set by caller
        frame._main_layout = section_layout
        
        # Create a wrapper widget to contain the layout
        wrapper = QWidget()
        wrapper.setLayout(section_layout)
        
        # Return frame with layout capability
        frame.setLayout(QVBoxLayout())
        frame.layout().addWidget(wrapper)
        
        return frame
    
    def export_inventory(self, format_type: str):
        """Export inventory."""
        try:
            items = InventoryQueries.get_all_items(self.session)
            
            filename = ExcelExporter.generate_filename("inventory_export")
            desktop = os.path.expanduser("~/Desktop")
            
            if format_type == "csv":
                filepath = os.path.join(desktop, f"{filename}.csv")
                ExcelExporter.export_inventory_csv(items, filepath)
            else:
                filepath = os.path.join(desktop, f"{filename}.xlsx")
                ExcelExporter.export_inventory_excel(items, filepath)
            
            QMessageBox.information(self, "Success", f"Exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def export_waste(self, format_type: str):
        """Export waste log."""
        try:
            logs = WasteQueries.get_recent_waste(self.session, limit=1000)
            
            filename = ExcelExporter.generate_filename("waste_log_export")
            desktop = os.path.expanduser("~/Desktop")
            
            filepath = os.path.join(desktop, f"{filename}.csv")
            ExcelExporter.export_waste_log_csv(logs, filepath)
            
            QMessageBox.information(self, "Success", f"Exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def generate_valuation_report(self):
        """Generate inventory valuation report."""
        try:
            items = InventoryQueries.get_all_items(self.session)
            total_value = sum(item.get_stock_value() for item in items)
            
            report = f"""
INVENTORY VALUATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================

Total Items: {len(items)}
Total Inventory Value: ${total_value:.2f}

Top 10 Most Valuable Items:
"""
            
            sorted_items = sorted(items, key=lambda x: x.get_stock_value(), reverse=True)[:10]
            for i, item in enumerate(sorted_items, 1):
                report += f"\n{i}. {item.name} - ${item.get_stock_value():.2f}"
            
            filename = f"valuation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(os.path.expanduser("~/Desktop"), filename)
            
            with open(filepath, 'w') as f:
                f.write(report)
            
            QMessageBox.information(self, "Success", f"Report generated:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Report generation failed: {e}")
