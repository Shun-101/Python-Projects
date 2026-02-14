"""
BrewMetric Dashboard Page
Analytics, charts, and overview of inventory status.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea
)
from database import User, DatabaseManager, InventoryQueries, WasteQueries
from ui.styles import Styles
from config import COLORS, DASHBOARD_REFRESH_INTERVAL


class DashboardPage(QWidget):
    """Dashboard page with analytics and overview."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        """
        Initialize dashboard page.
        
        Args:
            user: Current user
            db_manager: Database manager
        """
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(DASHBOARD_REFRESH_INTERVAL)
        
        # Initialize UI
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_items_label = self.create_stat_card("📦 Total Items", "0")
        self.low_stock_label = self.create_stat_card("⚠️ Low Stock", "0")
        self.expiring_label = self.create_stat_card("⏰ Expiring Soon", "0")
        self.total_value_label = self.create_stat_card("💰 Total Value", "$0.00")
        
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addWidget(self.low_stock_label)
        stats_layout.addWidget(self.expiring_label)
        stats_layout.addWidget(self.total_value_label)
        
        main_layout.addLayout(stats_layout)
        
        # Activity feed
        activity_label = QLabel("Recent Activity")
        activity_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        main_layout.addWidget(activity_label)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "User", "Action", "Item"])
        self.activity_table.setStyleSheet(Styles.get_global_stylesheet())
        self.activity_table.setMinimumHeight(300)
        self.activity_table.setMaximumHeight(400)
        main_layout.addWidget(self.activity_table)
        
        # Stretch
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def create_header(self) -> QWidget:
        """Create dashboard header."""
        header = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Welcome back! Here's an overview of your inventory.")
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header
    
    def create_stat_card(self, title: str, value: str) -> QFrame:
        """Create a statistics card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary_bg']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setObjectName("muted")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setObjectName("heading")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def refresh_data(self):
        """Refresh dashboard data."""
        try:
            # Get inventory stats
            all_items = InventoryQueries.get_all_items(self.session)
            low_stock = InventoryQueries.get_low_stock_items(self.session)
            expiring = InventoryQueries.get_expiring_items(self.session)
            total_value = InventoryQueries.get_total_inventory_value(self.session)
            
            # Update stat cards
            self.total_items_label.findChild(QLabel).setText(str(len(all_items)))
            self.low_stock_label.findChild(QLabel).setText(str(len(low_stock)))
            self.expiring_label.findChild(QLabel).setText(str(len(expiring)))
            self.total_value_label.findChild(QLabel).setText(f"${total_value:.2f}")
            
            # Update activity table (placeholder for now)
            self.activity_table.setRowCount(0)
        
        except Exception as e:
            print(f"[v0] Error refreshing dashboard: {e}")
    
    def closeEvent(self, event):
        """Handle close event."""
        self.refresh_timer.stop()
        self.session.close()
        super().closeEvent(event)
