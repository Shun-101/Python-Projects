# BrewMetric - Milk Tea Inventory & Monitoring System

A professional Python desktop application for managing milk tea shop inventory with modern UI, security, analytics, and audit capabilities.

## Features

- **Secure Authentication**: Password hashing with bcrypt and role-based access control
- **Inventory Management**: Full CRUD operations with stock alerts and expiration tracking
- **Waste Tracking**: Record spoilage and waste with automatic inventory updates
- **Audit Trail**: Comprehensive logging of all system actions (admin-only view)
- **Reports & Export**: Export inventory data and waste logs to CSV/Excel
- **Dark Mode UI**: Modern, professional dark theme with smooth animations
- **Real-time Dashboard**: Stock status, alerts, and activity feed
- **Cross-Platform**: Runs on Windows, Mac, and Linux

## Tech Stack

- **Frontend**: PySide6 (Qt for Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Security**: bcrypt for password hashing
- **Analytics**: Plotly for charts
- **Concurrency**: Python threading for smooth UI

## Requirements

- Python 3.10 or higher
- pip package manager

## Installation

### 1. Clone or Download the Project

```bash
cd brewmetric
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- PySide6 (Qt framework)
- SQLAlchemy (ORM)
- bcrypt (password hashing)
- openpyxl (Excel export)
- plotly (charts)
- python-dotenv (configuration)

## Running the Application

```bash
python main.py
```

The application will:
1. Initialize the database (if not already created)
2. Create a default admin account (if none exists)
3. Display the login window

### Default Credentials (First Login)

- **Username**: `admin`
- **Password**: `Admin@123456`

⚠️ **Important**: Change the default password immediately after first login!

## User Guide

### Login

1. Enter your username and password
2. The password strength indicator shows your password security level
3. Click "Login" to authenticate

### Dashboard

The dashboard shows:
- **Total Items**: Total inventory items
- **Low Stock**: Items below minimum threshold
- **Expiring Soon**: Items expiring within 7 days
- **Total Value**: Total monetary value of inventory
- **Recent Activity**: Latest actions in the system

### Inventory Management

**View Items**:
- Search by item name
- Filter by category
- See stock status (OK, LOW, EXPIRING, EXPIRED)

**Add Item**:
- Click "Add Item" button
- Fill in item details (name, category, quantity, cost, etc.)
- Save to database

**Edit Item**:
- Double-click on any item in the table
- Update details as needed
- Save changes

**Stock Status**:
- 🟢 Green: Healthy stock levels
- 🟡 Orange: Expiring within 7 days
- 🔴 Red: Below minimum threshold or expired

### Waste Log

Record waste and spoilage:
1. Click "Record Waste"
2. Select the item from dropdown
3. Enter quantity wasted
4. Select waste reason (Spill, Expired, Quality Issue, etc.)
5. Add optional notes
6. Save

The system automatically updates inventory quantity.

### Reports & Export

**Export Options**:
- **Inventory (CSV/Excel)**: All inventory items with stock status and values
- **Waste Log (CSV)**: Waste entries with user, date, and reason
- **Valuation Report**: Top items by monetary value (admin only)

**File Location**: Exports save to your Desktop by default

### Audit Trail (Admin Only)

View complete system activity log:
- Filter by action type (LOGIN, LOGOUT, CREATE, UPDATE, DELETE)
- Search audit entries
- Export to CSV for compliance

## Project Structure

```
brewmetric/
├── main.py                 # Application entry point
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── database/
│   ├── __init__.py
│   └── database.py         # SQLAlchemy models and queries
├── auth/
│   ├── __init__.py
│   └── auth.py             # Authentication and authorization
├── ui/
│   ├── __init__.py
│   ├── styles.py           # Global theming
│   ├── animations.py       # Animation utilities
│   ├── login_window.py     # Login UI
│   ├── main_window.py      # Main window and sidebar
│   ├── dashboard.py        # Dashboard page
│   ├── inventory.py        # Inventory management page
│   ├── waste_log.py        # Waste tracking page
│   ├── reports.py          # Export and reports page
│   └── audit_trail.py      # Audit log viewer (admin)
└── utils/
    ├── __init__.py
    ├── validators.py       # Input validation
    └── excel_export.py     # CSV/Excel export functionality
```

## Database

### Tables

- **users**: User accounts with roles (admin/staff)
- **inventory_items**: Product inventory with stock levels
- **waste_logs**: Waste and spoilage records
- **audit_trails**: Complete system action logs
- **activity_feed**: Recent actions for dashboard

### Database File

`brewmetric.db` - SQLite database file (created automatically)

## Security

### Password Requirements

- Minimum 8 characters
- At least 1 lowercase letter
- At least 1 uppercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*)

### Role-Based Access Control

**Admin**:
- Full CRUD on inventory
- View all audit trails
- Create/delete user accounts
- Generate all reports
- Adjust waste logs

**Staff**:
- Add and view inventory items
- Record waste entries
- View own activity only
- Export limited reports
- Cannot access audit trail

### Security Features

- Passwords hashed with bcrypt (salted, 12 rounds)
- SQL injection prevention (SQLAlchemy ORM)
- Session management
- Comprehensive audit logging
- File permission controls

## Customization

### Configuration (config.py)

You can customize:
- Window size and theme colors
- Stock alert thresholds
- Password requirements
- Audit retention period
- Export formats

### Adding Custom Categories

Edit `STOCK_CATEGORIES` in `config.py`:

```python
STOCK_CATEGORIES = ["Pearls", "Tea", "Syrups", "Milk", "Toppings", "Custom"]
```

### Adding Waste Reasons

Edit `WASTE_REASONS` in `config.py`:

```python
WASTE_REASONS = ["Spill", "Expired", "Quality Issue", "Damaged", "Custom"]
```

## Troubleshooting

### ImportError: No module named 'PySide6'

Install dependencies:
```bash
pip install -r requirements.txt
```

### Database Error

If the database becomes corrupted:
1. Stop the application
2. Delete `brewmetric.db`
3. Run the application again (it will recreate the database)

### Can't Login

- Verify username and password are correct
- Default credentials are `admin` / `Admin@123456`
- Check that user account is active

### Export Not Working

- Ensure Desktop folder exists
- Check file permissions
- Try exporting to a different location

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name BrewMetric main.py
```

The executable will be in the `dist/` folder.

## Development

### Running in Debug Mode

Add debug output in files:
```python
print("[v0] Debug message:", variable)
```

### Adding New Pages

1. Create new file in `ui/` folder
2. Create class extending `QWidget`
3. Implement `__init__` and `init_ui` methods
4. Add page to main_window.py's `create_content_pages()` method

## Performance Tips

- Use date filters in reports for faster queries
- Archived old waste logs to keep database small
- Close application properly (don't force quit)
- Run on SSD for better performance

## Future Enhancements

- Email reports and alerts
- Mobile app for mobile ordering
- Supplier management
- Customer analytics
- Multi-user cloud sync
- Barcode/QR code scanning

## License

Proprietary - BrewMetric

## Support

For issues or feature requests, please contact support.

---

**Version**: 1.0.0  
**Last Updated**: 2025
