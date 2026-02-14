"""
BrewMetric Configuration Module
Centralized configuration and constants for the application.
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "BrewMetric"
APP_VERSION = "1.0.0"
APP_TITLE = "BrewMetric - Milk Tea Inventory & Monitoring System"

# Paths
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "brewmetric.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# UI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
SIDEBAR_WIDTH = 60  # Icon-only sidebar width
SIDEBAR_EXPANDED_WIDTH = 250
MIN_THRESHOLD_DEFAULT = 10  # Default minimum stock threshold
EXPIRATION_ALERT_DAYS = 7  # Days before expiration to alert

# Theme Colors (Dark Mode)
COLORS = {
    "primary_bg": "#1e1e1e",      # Dark gray background
    "secondary_bg": "#2d2d2d",     # Lighter gray for cards
    "accent_green": "#00a86b",     # Healthy/success
    "warning_red": "#ff6b6b",      # Low stock/alert
    "caution_orange": "#ffa500",   # Near expiration
    "text_white": "#ffffff",       # Main text
    "text_muted": "#b0b0b0",       # Secondary text
    "border_color": "#3d3d3d",     # Border color
}

# Animation Timings (milliseconds)
ANIMATION_DURATION_FAST = 200
ANIMATION_DURATION_NORMAL = 300
ANIMATION_DURATION_SLOW = 500
ANIMATION_DURATION_SPLASH = 1000

# Authentication
PASSWORD_MIN_LENGTH = 8
BCRYPT_ROUNDS = 12

# Database
DATABASE_ECHO = False  # Set to True for SQL debugging
CONNECTION_TIMEOUT = 30

# Audit Trail
AUDIT_ENABLED = True
AUDIT_RETENTION_DAYS = 365  # Keep audit logs for 1 year

# Role Definitions
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"

# Stock Categories
STOCK_CATEGORIES = ["Pearls", "Tea", "Syrups", "Milk", "Toppings", "Other"]

# Waste Reasons
WASTE_REASONS = ["Spill", "Expired", "Quality Issue", "Damaged", "Other"]

# Export Settings
EXPORT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPORT_DECIMAL_PLACES = 2

# Dashboard Settings
DASHBOARD_REFRESH_INTERVAL = 30000  # Milliseconds (30 seconds)
DASHBOARD_ACTIVITY_FEED_LIMIT = 20
DASHBOARD_LOW_STOCK_LIMIT = 10
