# BrewMetric - Installation Guide

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- **RAM**: 512 MB minimum (1 GB recommended)
- **Disk Space**: 500 MB for Python + dependencies

## Step 1: Verify Prerequisites

### Check Python Installation

Open terminal/command prompt and run:

```bash
python --version
```

If you see Python 3.10 or higher, you're good to go. If not, download from [python.org](https://www.python.org/downloads/)

### Verify Setup

Run the verification script:

```bash
python verify_setup.py
```

This will check:
- ✅ Python version compatibility
- ✅ Required dependencies
- ✅ Project structure
- ✅ Database setup
- ✅ Module imports

## Step 2: Install Dependencies

### Option A: Automatic (Recommended)

```bash
pip install -r requirements.txt
```

This installs all required packages at once.

### Option B: Manual Installation

If the automatic method fails, install each package:

```bash
pip install PySide6==6.7.0
pip install SQLAlchemy==2.0.23
pip install bcrypt==4.1.1
pip install openpyxl==3.11.0
pip install plotly==5.18.0
pip install python-dotenv==1.0.0
```

### Option C: Using Virtual Environment (Best Practice)

Create an isolated Python environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

To deactivate the environment later, run:
```bash
deactivate
```

## Step 3: Verify Installation

Run the verification script again:

```bash
python verify_setup.py
```

All checks should show ✅

## Step 4: Run the Application

```bash
python main.py
```

The application window will appear with the login screen.

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Python version too old"

**Solution**: Update Python to 3.10+
- Download from [python.org](https://www.python.org/downloads/)
- On Windows: Run the installer with "Add Python to PATH" checked
- On Mac: Use `brew install python@3.10`
- On Linux: `sudo apt update && sudo apt install python3.10`

### Permission Denied on Linux/Mac

**Solution**: Use user install
```bash
pip install --user -r requirements.txt
```

### "No module named 'config'"

**Solution**: Ensure you're in the correct directory
```bash
cd brewmetric
python main.py
```

### Application Won't Start

**Solution**: Run verification script
```bash
python verify_setup.py
```

Fix any reported issues, then try again.

### "Cannot find database"

**Solution**: The database is created automatically on first run. If you get an error:
1. Delete `brewmetric.db` if it exists
2. Ensure the application directory is writable
3. Run `python main.py` again

### Port Already in Use (Network-related issues)

BrewMetric uses SQLite (local database) so this shouldn't occur. If you see this error, something else is wrong - check the verification script output.

## Advanced Setup

### Creating Executable

Package the application as a standalone executable:

```bash
pip install pyinstaller

# Create executable (in dist/ folder)
pyinstaller --onefile --windowed --name BrewMetric main.py

# To add an icon:
pyinstaller --onefile --windowed --icon=icon.png --name BrewMetric main.py
```

### Custom Configuration

Edit `config.py` to customize:
- Theme colors
- Window size
- Stock alert thresholds
- Password requirements
- Stock categories
- Waste reasons

### Database Location

By default, the database is created in the application directory as `brewmetric.db`

To use a different location, edit `config.py`:
```python
DATABASE_PATH = Path("/custom/path/brewmetric.db")
```

## Performance Optimization

### For Slower Computers

1. Close unnecessary applications
2. Ensure at least 1 GB free RAM
3. Run on SSD if possible
4. Disable animations (edit `config.py`):
   ```python
   ANIMATION_DURATION_NORMAL = 0  # Disable animations
   ```

### For Faster Performance

1. Close other applications
2. Keep inventory database small (archive old records)
3. Use SSD storage
4. Ensure Python is up to date

## Uninstallation

### Remove Virtual Environment

```bash
# On Windows:
rmdir /s venv

# On Mac/Linux:
rm -rf venv
```

### Remove Application

```bash
rm -rf brewmetric
```

### Remove Global Dependencies

```bash
pip uninstall PySide6 SQLAlchemy bcrypt openpyxl plotly python-dotenv
```

## Getting Help

1. **Check Errors**: Look at console output for error messages
2. **Run Verification**: `python verify_setup.py` shows what's broken
3. **Check Logs**: Application prints debug info with `[v0]` prefix
4. **Read Documentation**: See README.md for common issues

## Next Steps

After successful installation:

1. Run the application: `python main.py`
2. Login with default credentials:
   - Username: `admin`
   - Password: `Admin@123456`
3. Read [QUICKSTART.md](QUICKSTART.md) for a quick overview
4. Read [README.md](README.md) for detailed documentation
5. Change the default admin password immediately!

---

## Version Information

- **BrewMetric**: v1.0.0
- **Python**: 3.10+
- **Last Updated**: 2025

## Support

For installation issues:
1. Run `python verify_setup.py`
2. Read troubleshooting section above
3. Check that all files are in correct directory
4. Ensure you have write permissions in the directory
