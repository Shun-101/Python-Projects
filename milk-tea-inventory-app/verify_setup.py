#!/usr/bin/env python3
"""
BrewMetric Setup Verification Script
Checks that all dependencies and requirements are met.
"""

import sys
import importlib
import platform


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Current Python: {version_str}")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ ERROR: Python 3.10+ required")
        return False
    
    print("✅ Python version is compatible")
    return True


def check_dependency(package_name, import_name=None):
    """Check if a dependency is installed."""
    import_name = import_name or package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name:<20} {version}")
        return True
    except ImportError:
        print(f"❌ {package_name:<20} NOT INSTALLED")
        return False


def check_dependencies():
    """Check all required dependencies."""
    print_header("Dependency Check")
    
    dependencies = [
        ("PySide6", "PySide6"),
        ("SQLAlchemy", "sqlalchemy"),
        ("bcrypt", "bcrypt"),
        ("openpyxl", "openpyxl"),
        ("plotly", "plotly"),
        ("python-dotenv", "dotenv"),
    ]
    
    results = []
    for package, import_name in dependencies:
        results.append(check_dependency(package, import_name))
    
    if all(results):
        print("\n✅ All dependencies installed")
        return True
    else:
        print("\n❌ Some dependencies missing")
        print("Run: pip install -r requirements.txt")
        return False


def check_project_structure():
    """Check project structure."""
    print_header("Project Structure Check")
    
    import os
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "database/__init__.py",
        "database/database.py",
        "auth/__init__.py",
        "auth/auth.py",
        "ui/__init__.py",
        "ui/styles.py",
        "ui/animations.py",
        "ui/login_window.py",
        "ui/main_window.py",
        "ui/dashboard.py",
        "ui/inventory.py",
        "ui/waste_log.py",
        "ui/reports.py",
        "ui/audit_trail.py",
        "utils/__init__.py",
        "utils/validators.py",
        "utils/excel_export.py",
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file:<40} MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} files")
        return False
    else:
        print("\n✅ All required files present")
        return True


def check_database():
    """Check database setup."""
    print_header("Database Check")
    
    import os
    from config import DATABASE_PATH
    
    if os.path.exists(DATABASE_PATH):
        size = os.path.getsize(DATABASE_PATH)
        print(f"✅ Database found: {DATABASE_PATH}")
        print(f"   Size: {size:,} bytes")
        return True
    else:
        print(f"⚠️  Database not found: {DATABASE_PATH}")
        print("   It will be created on first run")
        return True


def run_integrity_test():
    """Run basic integrity test."""
    print_header("Integrity Test")
    
    try:
        print("Testing imports...")
        from config import APP_TITLE, APP_VERSION
        print(f"✅ Config import successful")
        print(f"   App: {APP_TITLE} v{APP_VERSION}")
        
        from database import DatabaseManager, User, InventoryItem
        print(f"✅ Database models import successful")
        
        from auth import AuthManager
        print(f"✅ Auth module import successful")
        
        from ui.styles import Styles
        print(f"✅ UI styles import successful")
        
        from utils import Validators, ExcelExporter
        print(f"✅ Utils import successful")
        
        print("\n✅ All integrity tests passed")
        return True
    
    except Exception as e:
        print(f"\n❌ Integrity test failed: {e}")
        return False


def main():
    """Run all checks."""
    print(f"\n{'='*60}")
    print("  BrewMetric - Setup Verification")
    print(f"{'='*60}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Database Setup", check_database),
        ("Integrity Test", run_integrity_test),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Everything is ready! Run: python main.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
