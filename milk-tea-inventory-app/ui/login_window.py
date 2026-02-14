"""
BrewMetric Login Window
Authentication UI with password validation and security.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QProgressBar, QMessageBox
)
from database import User, DatabaseManager
from auth import AuthManager
from ui.styles import Styles
from ui.animations import AnimationManager, ThreadManager
from config import APP_TITLE


class LoginWindow(QDialog):
    """Login window for user authentication."""
    
    # Signal emitted when login is successful
    login_successful = Signal(User)
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize login window.
        
        Args:
            db_manager: Database manager instance
        """
        super().__init__()
        self.db_manager = db_manager
        self.session = db_manager.get_session()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 400, 550)
        self.setModal(True)
        
        # Apply global stylesheet
        self.setStyleSheet(Styles.get_global_stylesheet())
        
        # Initialize UI
        self.init_ui()
        
        # Fade in animation on launch
        self.setWindowOpacity(0)
        AnimationManager.fade_in_widget(self, duration=1000)
    
    def init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("BrewMetric")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Milk Tea Inventory & Monitoring System")
        subtitle.setObjectName("subheading")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Separator
        main_layout.addSpacing(20)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 11))
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        main_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11))
        main_layout.addWidget(password_label)
        
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        password_layout.addWidget(self.password_input)
        
        # Show password toggle
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setMaximumWidth(50)
        self.show_password_btn.setMinimumHeight(40)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)
        
        password_container = QVBoxLayout()
        password_container.addLayout(password_layout)
        main_layout.addLayout(password_container)
        
        # Password strength indicator
        strength_label = QLabel("Password Strength")
        strength_label.setFont(QFont("Segoe UI", 9))
        strength_label.setObjectName("muted")
        main_layout.addWidget(strength_label)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximumHeight(8)
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {{'primary_bg'}};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: #ff6b6b;
                border-radius: 4px;
            }}
        """)
        self.password_input.textChanged.connect(self.update_password_strength)
        main_layout.addWidget(self.strength_bar)
        
        # Remember me checkbox
        self.remember_me = QCheckBox("Remember me")
        self.remember_me.setStyleSheet(f"""
            QCheckBox {{
                color: {{'text_muted'}};
                font-size: 10pt;
            }}
        """)
        main_layout.addWidget(self.remember_me)
        
        # Spacing
        main_layout.addSpacing(10)
        
        # Error message label
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        main_layout.addWidget(self.error_label)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(45)
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)
        
        # Loading indicator
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setText("Logging in...")
        self.loading_label.setVisible(False)
        main_layout.addWidget(self.loading_label)
        
        # Info section
        main_layout.addSpacing(15)
        info_label = QLabel("Default Credentials (First Login)")
        info_label.setObjectName("muted")
        info_label.setFont(QFont("Segoe UI", 9))
        main_layout.addWidget(info_label)
        
        creds_label = QLabel("Username: <b>admin</b><br>Password: <b>Admin@123456</b>")
        creds_label.setObjectName("muted")
        creds_label.setFont(QFont("Segoe UI", 9))
        creds_label.setWordWrap(True)
        main_layout.addWidget(creds_label)
        
        # Stretch to bottom
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁")
    
    def update_password_strength(self):
        """Update password strength indicator."""
        password = self.password_input.text()
        
        if not password:
            self.strength_bar.setValue(0)
            return
        
        strength = 0
        
        # Length check
        if len(password) >= 8:
            strength += 20
        if len(password) >= 12:
            strength += 10
        
        # Character variety
        if any(c.islower() for c in password):
            strength += 15
        if any(c.isupper() for c in password):
            strength += 15
        if any(c.isdigit() for c in password):
            strength += 15
        if any(c in "!@#$%^&*" for c in password):
            strength += 15
        
        self.strength_bar.setValue(min(strength, 100))
        
        # Change color based on strength
        if strength < 40:
            color = "#ff6b6b"  # Red
        elif strength < 70:
            color = "#ffa500"  # Orange
        else:
            color = "#00a86b"  # Green
        
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #2d2d2d;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Clear previous errors
        self.error_label.setText("")
        
        # Validate inputs
        if not username or not password:
            self.error_label.setText("Please enter username and password")
            return
        
        # Disable button and show loading
        self.login_button.setEnabled(False)
        self.loading_label.setVisible(True)
        
        # Run authentication in background thread
        ThreadManager.run_in_thread(
            self.authenticate_user,
            username,
            password,
            on_complete=self.on_login_complete,
            on_error=self.on_login_error
        )
    
    def authenticate_user(self, username: str, password: str):
        """
        Authenticate user (runs in background thread).
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Authenticated user or None
        """
        user = AuthManager.authenticate_user(self.session, username, password)
        return user
    
    def on_login_complete(self, user: User):
        """
        Handle successful login.
        
        Args:
            user: Authenticated user object
        """
        if user:
            # Set current user
            AuthManager.set_current_user(user, self.session)
            
            # Emit signal
            self.login_successful.emit(user)
            
            # Close dialog
            self.accept()
        else:
            self.on_login_error(Exception("Invalid credentials"))
    
    def on_login_error(self, error: Exception):
        """
        Handle login error.
        
        Args:
            error: Exception object
        """
        # Re-enable button
        self.login_button.setEnabled(True)
        self.loading_label.setVisible(False)
        
        error_msg = str(error)
        if "Invalid credentials" in error_msg or not error_msg:
            self.error_label.setText("Invalid username or password")
        else:
            self.error_label.setText(f"Login error: {error_msg}")
        
        print(f"[v0] Login error: {error}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.session.close()
        super().closeEvent(event)
