# 🍴 Kitchen Utensils Borrowing System

A comprehensive Python-based kitchen utensils borrowing management system with a modern GUI interface, admin controls, and advanced features for professional equipment tracking.

## Features

### 🎯 Core Features
- **User-friendly GUI** built with Tkinter
- **Borrow & Return System** with complete tracking
- **Real-time Inventory Tracking** with availability status
- **Dashboard** with statistics and overdue alerts
- **Complete Borrowing History** with search and filter
- **Admin Panel** with full CRUD operations

### 🔐 Security
- **Admin-Only Access** - System requires admin authentication
- **Password Hashing** using SHA-256
- **Change Password** functionality for admins

### ⏰ Trial Period
- **30-day free trial** from first run
- **Automatic expiration** after trial period
- **Trial countdown** displayed on login screen

### 👨‍💼 Admin Capabilities
- Add new kitchen utensils with categories
- Edit existing utensils (name, category, quantity)
- Delete utensils (only if not borrowed)
- View complete inventory status with filtering
- Track all borrowings with full contact details
- Change admin password
- Export borrowing records to CSV

### 📊 Advanced Borrowing Features
- **Due Date Tracking** - Set return deadlines for each loan
- **Overdue Detection** - Automatic identification of late returns
- **Contact Management** - Store phone and email for borrowers
- **Item Categories** - Organize utensils (Cutlery, Cookware, etc.)
- **Condition Tracking** - Record item condition on return
- **Notes & Remarks** - Add notes to borrowing records
- **Search & Filter** - Find borrowings by name, item, or status
- **Item History** - View complete borrowing history per item
- **Color Coding** - Visual indicators for overdue, active, and returned items
- **CSV Export** - Export all borrowing records for reporting

### 📈 Dashboard Features
- Total utensils count
- Available vs borrowed statistics
- Active loans tracking
- Overdue items alert section
- Recent activity feed
- Real-time status updates

## Installation

### Prerequisites
- Python 3.7 or higher
- Tkinter (usually comes with Python)

### Setup
1. Download the `kitchen_borrowing_system.py` file
2. Run the program:
\`\`\`bash
python scripts/kitchen_borrowing_system.py
\`\`\`

## Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the default password immediately after first login!

## Usage

### First Time Setup
1. Run the program - this starts your 30-day trial
2. Login with admin credentials
3. The system creates a `kitchen_system_data` folder automatically
4. Change the default admin password

### Dashboard
1. Login as admin
2. View the dashboard for system overview
3. See statistics: total utensils, available, borrowed, active loans, overdue items
4. Check overdue items section for late returns
5. Review recent activity

### Borrowing Utensils
1. Select "Borrow Utensil" from main menu
2. Enter borrower's name
3. Provide contact information (phone or email)
4. Select utensil and quantity
5. Set return due date (default 7 days)
6. Add optional notes
7. Confirm borrowing

### Returning Utensils
1. Select "Return Utensil" from main menu
2. Choose the borrowing record to return
3. Select item condition (Excellent, Good, Fair, Damaged, Lost)
4. Add return notes if needed
5. Confirm return

### Searching Borrowings
1. Select "Search Borrowings" from main menu
2. Filter by borrower name, utensil name, or status
3. View filtered results with color coding
4. Export results if needed

### Managing Equipment
1. Access "Manage Equipment" from main menu
2. Add new utensils with name, category, and quantity
3. Edit existing utensils (name, category, or quantity)
4. Delete utensils (only if not currently borrowed)
5. View complete inventory with borrowed counts

### Viewing Item History
1. Go to "View All Utensils"
2. Select a utensil from the list
3. Click "View Item History"
4. See complete borrowing history for that item

### Exporting Data
1. Go to "Borrowing History"
2. Click "Export to CSV"
3. Choose save location
4. Open in Excel or any spreadsheet application

## Data Storage

All data is stored locally in JSON files in the `kitchen_system_data` folder:
- `utensils.json` - Kitchen utensils inventory with categories
- `borrowings.json` - Complete borrowing records with contact info, due dates, and notes
- `admin.json` - Admin credentials (hashed)
- `trial.json` - Trial period information

**No internet connection required** - All data is stored locally on your computer.

## Color Coding

The system uses color coding for easy status identification:
- **Red/Pink Background** - Overdue items (past due date)
- **Yellow Background** - Active borrowings (not yet returned)
- **Green Background** - Returned items (completed)

## Trial Period

- **Duration:** 30 days from first run
- **Countdown:** Displayed on login screen
- **Expiration:** Program becomes unusable after trial ends
- **Reset:** Delete the `kitchen_system_data` folder to reset trial (for testing purposes)

## Security Notes

- Admin passwords are hashed using SHA-256
- Default admin password should be changed immediately
- Trial period is enforced at application startup
- Data files are stored locally in JSON format
- Only admin access is allowed - no regular user accounts

## System Requirements

- **OS:** Windows, macOS, or Linux
- **Python:** 3.7+
- **RAM:** 256 MB minimum
- **Storage:** 10 MB for application and data
- **Internet:** Not required (fully offline system)

## Troubleshooting

**Program won't start:**
- Ensure Python 3.7+ is installed
- Check if Tkinter is available: `python -m tkinter`

**Trial expired:**
- Contact support or delete `kitchen_system_data/trial.json` for testing

**Can't login:**
- Default credentials: admin/admin123
- Check if `admin.json` exists in data folder
- Ensure you're using the correct admin credentials

**Can't delete utensil:**
- Utensils with active borrowings cannot be deleted
- Return all borrowed items first, then delete

**Can't edit quantity below borrowed amount:**
- System prevents setting total quantity below currently borrowed amount
- Return items first or increase quantity

## Sample Data

The system comes pre-loaded with sample kitchen utensils:
- Chef Knife (5 units) - Cutlery
- Cutting Board (8 units) - Preparation
- Mixing Bowl (10 units) - Cookware
- Whisk (6 units) - Utensils
- Spatula (7 units) - Utensils

You can modify or delete these and add your own equipment.

## Categories

Available utensil categories:
- Cutlery
- Cookware
- Preparation
- Utensils
- Bakeware
- Storage
- Other

## Best Practices

1. **Set Realistic Due Dates** - Consider the typical usage period for each item
2. **Track Contact Information** - Always collect phone or email for follow-ups
3. **Monitor Overdue Items** - Check dashboard regularly for late returns
4. **Record Condition** - Document item condition on return to track wear
5. **Use Notes** - Add relevant details about special circumstances
6. **Regular Backups** - Copy the `kitchen_system_data` folder periodically
7. **Export Reports** - Use CSV export for record-keeping and analysis

## License

This is a trial version. Contact support for full version licensing.

---

**Note:** This system includes a 30-day trial period. After expiration, the program will not run until a valid license is obtained.
