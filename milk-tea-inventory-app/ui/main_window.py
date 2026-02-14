"""
BrewMetric Main Application Window
Main window with sidebar navigation and content area.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QMessageBox, QScrollArea
)
from database import User, DatabaseManager, AuditTrail, ROLE_ADMIN
from auth import AuthManager
from ui.styles import Styles
from ui.animations import AnimationManager
from config import (
    APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH,
    SIDEBAR_EXPANDED_WIDTH, COLORS
)


class MainWindow(QMainWindow):
    """Main application window with sidebar and content area."""
    
    def __init__(self, user: User, db_manager: DatabaseManager):
        """
        Initialize main window.
        
        Args:
            user: Authenticated user
            db_manager: Database manager instance
        """
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.sidebar_expanded = False
        self.current_page = None
        
        # Window settings
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(1000, 700)
        
        # Apply stylesheet
        self.setStyleSheet(Styles.get_global_stylesheet())
        
        # Initialize UI
        self.init_ui()
        
        # Log login action
        self.log_audit_action("LOGIN", "User", user.id, f"User '{user.username}' logged in")
        
        # Fade in animation
        self.setWindowOpacity(0)
        AnimationManager.fade_in_widget(self, duration=800)
    
    def init_ui(self):
        """Initialize main UI."""
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 0)
        
        # Create content area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['primary_bg']};
                border: none;
            }}
        """)
        
        # Add placeholder pages (will be populated later)
        self.create_content_pages()
        
        main_layout.addWidget(self.content_stack, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_sidebar(self) -> QFrame:
        """
        Create navigation sidebar.
        
        Returns:
            Sidebar frame widget
        """
        sidebar = QFrame()
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary_bg']};
                border-right: 1px solid {COLORS['border_color']};
            }}
        """)
        sidebar.setMaximumWidth(SIDEBAR_EXPANDED_WIDTH)
        sidebar.setMinimumWidth(SIDEBAR_WIDTH)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(10)
        
        # Logo/Title
        logo_label = QLabel("📊")
        logo_label.setFont(QFont("Segoe UI", 20))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        title_label = QLabel("BrewMetric")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setStyleSheet(f"background-color: {COLORS['border_color']}; height: 1px;")
        layout.addWidget(separator)
        
        # Navigation buttons
        nav_buttons = [
            ("📈", "Dashboard", "dashboard"),
            ("📦", "Inventory", "inventory"),
            ("🗑️", "Waste Log", "waste"),
            ("📊", "Reports", "reports"),
        ]
        
        # Add admin-only buttons
        if self.user.role == ROLE_ADMIN:
            nav_buttons.append(("🔐", "Audit Trail", "audit"))
        
        self.nav_buttons = {}
        for icon, label, key in nav_buttons:
            btn = self.create_nav_button(icon, label, key)
            layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        # Spacing
        layout.addStretch()
        
        # User info section
        user_section_separator = QFrame()
        user_section_separator.setStyleSheet(f"background-color: {COLORS['border_color']}; height: 1px;")
        layout.addWidget(user_section_separator)
        
        # Current user info
        user_label = QLabel(f"👤 {self.user.full_name}")
        user_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        user_label.setWordWrap(True)
        user_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_label)
        
        role_label = QLabel(f"({self.user.role.upper()})")
        role_label.setObjectName("muted")
        role_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(role_label)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setMinimumHeight(35)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning_red']};
                color: {COLORS['text_white']};
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                margin: 0 5px;
            }}
            QPushButton:hover {{
                background-color: #ff8383;
            }}
        """)
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_nav_button(self, icon: str, label: str, key: str) -> QPushButton:
        """
        Create a navigation button.
        
        Args:
            icon: Emoji icon
            label: Button label
            key: Page identifier
            
        Returns:
            Navigation button
        """
        btn = QPushButton(f"{icon} {label}")
        btn.setMinimumHeight(45)
        btn.setFont(QFont("Segoe UI", 10))
        btn.setStyleSheet(Styles.get_sidebar_button_style(active=False))
        btn.clicked.connect(lambda: self.switch_page(key))
        return btn
    
    def create_content_pages(self):
        """Create content pages."""
        # Import page modules here to avoid circular imports
        from ui.dashboard import DashboardPage
        from ui.inventory import InventoryPage
        from ui.waste_log import WasteLogPage
        from ui.reports import ReportsPage
        
        # Create pages
        self.pages = {
            "dashboard": DashboardPage(self.user, self.db_manager),
            "inventory": InventoryPage(self.user, self.db_manager),
            "waste": WasteLogPage(self.user, self.db_manager),
            "reports": ReportsPage(self.user, self.db_manager),
        }
        
        # Add audit trail page if admin
        if self.user.role == ROLE_ADMIN:
            from ui.audit_trail import AuditTrailPage
            self.pages["audit"] = AuditTrailPage(self.user, self.db_manager)
        
        # Add pages to stack widget
        for key, page in self.pages.items():
            self.content_stack.addWidget(page)
        
        # Default to dashboard
        self.switch_page("dashboard")
    
    def switch_page(self, page_key: str):
        """
        Switch to a different content page.
        
        Args:
            page_key: Page identifier
        """
        if page_key not in self.pages:
            return
        
        # Update button styles
        for key, btn in self.nav_buttons.items():
            is_active = (key == page_key)
            btn.setStyleSheet(Styles.get_sidebar_button_style(active=is_active))
        
        # Switch page
        page = self.pages[page_key]
        self.content_stack.setCurrentWidget(page)
        self.current_page = page_key
        
        # Animate
        AnimationManager.fade_in_widget(page, duration=300)
    
    def log_audit_action(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        description: str = None,
        old_values: str = None,
        new_values: str = None
    ):
        """
        Log an action to audit trail.
        
        Args:
            action: Action type (LOGIN, LOGOUT, CREATE, UPDATE, DELETE)
            entity_type: Type of entity affected
            entity_id: ID of entity
            description: Description of action
            old_values: Old values (JSON string)
            new_values: New values (JSON string)
        """
        try:
            audit_trail = AuditTrail(
                user_id=self.user.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                old_values=old_values,
                new_values=new_values
            )
            self.session.add(audit_trail)
            self.session.commit()
        except Exception as e:
            print(f"[v0] Error logging audit action: {e}")
    
    def handle_logout(self):
        """Handle logout action."""
        # Confirm logout
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Log logout action
        self.log_audit_action("LOGOUT", "User", self.user.id, f"User '{self.user.username}' logged out")
        
        # Clear session
        AuthManager.logout()
        self.session.close()
        
        # Close window
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.session.close()
        super().closeEvent(event)
