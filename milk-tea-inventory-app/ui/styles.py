"""
BrewMetric UI Styles Module
Centralized theming and styling for all UI components.
"""

from config import COLORS, ANIMATION_DURATION_NORMAL

class Styles:
    """Centralized styling constants and stylesheets."""
    
    # ========================================================================
    # Global Stylesheet
    # ========================================================================
    
    @staticmethod
    def get_global_stylesheet() -> str:
        """Get the global application stylesheet."""
        return f"""
            * {{
                margin: 0;
                padding: 0;
                border: none;
            }}
            
            QWidget {{
                background-color: {COLORS['primary_bg']};
                color: {COLORS['text_white']};
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 11pt;
            }}
            
            QMainWindow {{
                background-color: {COLORS['primary_bg']};
            }}
            
            QDialog {{
                background-color: {COLORS['secondary_bg']};
                border-radius: 8px;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['primary_bg']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
                cursor: pointer;
            }}
            
            QPushButton:hover {{
                background-color: #00c97d;
                border: 2px solid {COLORS['accent_green']};
            }}
            
            QPushButton:pressed {{
                background-color: #008c5b;
            }}
            
            QPushButton:disabled {{
                background-color: {COLORS['text_muted']};
                color: {COLORS['primary_bg']};
            }}
            
            QPushButton#dangerButton {{
                background-color: {COLORS['warning_red']};
            }}
            
            QPushButton#dangerButton:hover {{
                background-color: #ff8383;
                border: 2px solid {COLORS['warning_red']};
            }}
            
            QPushButton#warningButton {{
                background-color: {COLORS['caution_orange']};
            }}
            
            QPushButton#warningButton:hover {{
                background-color: #ffb84d;
                border: 2px solid {COLORS['caution_orange']};
            }}
            
            /* Line Edits (Text Fields) */
            QLineEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                border: 2px solid {COLORS['border_color']};
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            QLineEdit:disabled {{
                background-color: {COLORS['primary_bg']};
                color: {COLORS['text_muted']};
            }}
            
            /* Text Edits (Multi-line) */
            QTextEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                border: 2px solid {COLORS['border_color']};
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }}
            
            QTextEdit:focus {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            /* Combo Boxes (Dropdowns) */
            QComboBox {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                border: 2px solid {COLORS['border_color']};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 11pt;
            }}
            
            QComboBox:focus {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: url(:/arrow-down);
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                selection-background-color: {COLORS['accent_green']};
                border: 2px solid {COLORS['border_color']};
            }}
            
            /* Tables */
            QTableWidget {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                gridline-color: {COLORS['border_color']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 6px;
            }}
            
            QTableWidget::item {{
                padding: 6px;
                border: none;
                border-bottom: 1px solid {COLORS['border_color']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['primary_bg']};
            }}
            
            QHeaderView::section {{
                background-color: {COLORS['primary_bg']};
                color: {COLORS['text_white']};
                padding: 6px;
                border: none;
                border-right: 1px solid {COLORS['border_color']};
                font-weight: bold;
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background-color: {COLORS['primary_bg']};
                border: none;
                width: 12px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border_color']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_muted']};
            }}
            
            QScrollBar:horizontal {{
                background-color: {COLORS['primary_bg']};
                border: none;
                height: 12px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['border_color']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {COLORS['text_muted']};
            }}
            
            /* Labels */
            QLabel {{
                color: {COLORS['text_white']};
                font-size: 11pt;
            }}
            
            QLabel#heading {{
                font-size: 16pt;
                font-weight: bold;
                color: {COLORS['text_white']};
            }}
            
            QLabel#subheading {{
                font-size: 12pt;
                font-weight: bold;
                color: {COLORS['text_white']};
            }}
            
            QLabel#muted {{
                color: {COLORS['text_muted']};
                font-size: 10pt;
            }}
            
            QLabel#errorLabel {{
                color: {COLORS['warning_red']};
                font-weight: bold;
            }}
            
            QLabel#warningLabel {{
                color: {COLORS['caution_orange']};
                font-weight: bold;
            }}
            
            QLabel#successLabel {{
                color: {COLORS['accent_green']};
                font-weight: bold;
            }}
            
            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                border: 2px solid {COLORS['border_color']};
                border-radius: 6px;
                padding: 6px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            /* Check Boxes */
            QCheckBox {{
                color: {COLORS['text_white']};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border_color']};
                border-radius: 4px;
                background-color: {COLORS['secondary_bg']};
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent_green']};
                border: 2px solid {COLORS['accent_green']};
            }}
            
            /* Radio Buttons */
            QRadioButton {{
                color: {COLORS['text_white']};
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border_color']};
                border-radius: 9px;
                background-color: {COLORS['secondary_bg']};
            }}
            
            QRadioButton::indicator:hover {{
                border: 2px solid {COLORS['accent_green']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {COLORS['accent_green']};
                border: 2px solid {COLORS['accent_green']};
            }}
            
            /* Frames and Grouping */
            QFrame {{
                background-color: {COLORS['secondary_bg']};
                border-radius: 6px;
            }}
            
            QGroupBox {{
                background-color: {COLORS['secondary_bg']};
                border: 2px solid {COLORS['border_color']};
                border-radius: 6px;
                padding-top: 12px;
                margin-top: 6px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_muted']};
                border-top: 1px solid {COLORS['border_color']};
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {COLORS['primary_bg']};
                color: {COLORS['text_white']};
                border-bottom: 1px solid {COLORS['border_color']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {COLORS['secondary_bg']};
            }}
            
            QMenu {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_white']};
                border: 1px solid {COLORS['border_color']};
            }}
            
            QMenu::item:selected {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['primary_bg']};
            }}
        """
    
    # ========================================================================
    # Component-Specific Styles
    # ========================================================================
    
    @staticmethod
    def get_sidebar_button_style(active: bool = False) -> str:
        """Get style for sidebar navigation buttons."""
        bg_color = COLORS['accent_green'] if active else COLORS['secondary_bg']
        text_color = COLORS['primary_bg'] if active else COLORS['text_white']
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                margin: 4px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['accent_green']};
                color: {COLORS['primary_bg']};
            }}
        """
    
    @staticmethod
    def get_card_style() -> str:
        """Get style for card/panel containers."""
        return f"""
            QFrame {{
                background-color: {COLORS['secondary_bg']};
                border: 1px solid {COLORS['border_color']};
                border-radius: 8px;
                padding: 12px;
            }}
        """
    
    @staticmethod
    def get_success_style() -> str:
        """Get style for success elements."""
        return f"""
            background-color: {COLORS['accent_green']};
            color: {COLORS['primary_bg']};
        """
    
    @staticmethod
    def get_warning_style() -> str:
        """Get style for warning elements."""
        return f"""
            background-color: {COLORS['caution_orange']};
            color: {COLORS['primary_bg']};
        """
    
    @staticmethod
    def get_danger_style() -> str:
        """Get style for danger/error elements."""
        return f"""
            background-color: {COLORS['warning_red']};
            color: {COLORS['text_white']};
        """
    
    @staticmethod
    def get_low_stock_row_style() -> str:
        """Get style for low stock table rows."""
        return f"""
            background-color: {COLORS['warning_red']};
            color: {COLORS['text_white']};
        """
    
    @staticmethod
    def get_expiring_soon_row_style() -> str:
        """Get style for expiring soon table rows."""
        return f"""
            background-color: {COLORS['caution_orange']};
            color: {COLORS['primary_bg']};
        """
    
    @staticmethod
    def get_healthy_stock_row_style() -> str:
        """Get style for healthy stock table rows."""
        return f"""
            background-color: {COLORS['accent_green']};
            color: {COLORS['primary_bg']};
        """
