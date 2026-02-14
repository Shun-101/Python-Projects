"""
BrewMetric Application Entry Point
Main application launcher with database initialization.
"""

import sys
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QTimer

from database import DatabaseManager
from auth import AuthManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.styles import Styles
from config import APP_TITLE, APP_VERSION, DATABASE_PATH


class BrewMetricApp:
    """Main application controller."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.db_manager = None
        self.login_window = None
        self.main_window = None
    
    def initialize_database(self) -> bool:
        """
        Initialize database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"[v0] Initializing database at {DATABASE_PATH}")
            self.db_manager = DatabaseManager()
            self.db_manager.init_db()
            
            # Create default admin if needed
            session = self.db_manager.get_session()
            admin = AuthManager.create_default_admin(session)
            
            if admin:
                print(f"[v0] Default admin user is ready (or already exists)")
                print(f"[v0] Default credentials:")
                print(f"[v0]   Username: admin")
                print(f"[v0]   Password: Admin@123456")
            
            session.close()
            return True
        
        except Exception as e:
            error_msg = f"Failed to initialize database:\n{str(e)}"
            print(f"[v0] {error_msg}")
            QMessageBox.critical(None, "Database Error", error_msg)
            return False
    
    def show_login(self):
        """Show login window."""
        try:
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.login_successful.connect(self.on_login_success)
            self.login_window.exec()
        
        except Exception as e:
            print(f"[v0] Error showing login window: {e}")
            QMessageBox.critical(None, "Error", f"Failed to show login window:\n{str(e)}")
            sys.exit(1)
    
    def on_login_success(self, user):
        """
        Handle successful login.
        
        Args:
            user: Authenticated user object
        """
        try:
            # Create and show main window
            self.main_window = MainWindow(user, self.db_manager)
            self.main_window.show()
            
            # Close login window
            if self.login_window:
                self.login_window.close()
        
        except Exception as e:
            print(f"[v0] Error opening main window: {e}")
            QMessageBox.critical(None, "Error", f"Failed to open main window:\n{str(e)}")
            self.show_login()
    
    def run(self):
        """Run the application."""
        print(f"[v0] Starting {APP_TITLE} v{APP_VERSION}")
        
        # Initialize database
        if not self.initialize_database():
            return 1
        
        # Apply global stylesheet
        self.app.setStyle('Fusion')
        
        # Show login window
        self.show_login()
        
        # Run application
        return self.app.exec()


def main():
    """Main entry point."""
    app = BrewMetricApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
