# BrewMetric - Quick Start Guide

Get BrewMetric running in 5 minutes.

## Step 1: Install Python

Ensure you have Python 3.10+ installed:
```bash
python --version
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Wait for all packages to install (takes 1-2 minutes).

## Step 3: Run the Application

```bash
python main.py
```

The login window will appear.

## Step 4: Login

Use the default credentials:
- **Username**: `admin`
- **Password**: `Admin@123456`

## Step 5: Explore!

Welcome to BrewMetric! The dashboard shows your inventory overview.

### Quick Actions

1. **Add Inventory Item**: Click "Add Item" in Inventory tab
2. **Record Waste**: Click "Record Waste" in Waste Log tab
3. **View Reports**: Go to Reports tab and export CSV/Excel
4. **Check Audit Log**: Go to Audit Trail (admin only)

---

## Common Issues

### "ModuleNotFoundError: No module named 'PySide6'"

Run:
```bash
pip install -r requirements.txt
```

### Database Error on Startup

The database will be created automatically. If you get an error:
1. Delete `brewmetric.db` if it exists
2. Run `python main.py` again

### Can't Login

- Username: `admin`
- Password: `Admin@123456`
- Check that both fields are filled correctly

---

## Next Steps

- Read the full [README.md](README.md) for comprehensive documentation
- Change the default admin password immediately
- Add inventory items
- Set up waste tracking

Enjoy using BrewMetric!
