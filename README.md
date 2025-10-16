# 🧾 Invoice Management System

A complete invoice management solution built with Python, Streamlit, and SQLite. Create, track, and manage invoices with built-in analytics and PDF generation.

## 🎯 Features

### Core Functionality
- ✅ **Create Invoices** - Professional invoice generation with line items
- 📝 **Edit Invoices** - Update existing invoices anytime
- 🗑️ **Delete Invoices** - Remove invoices with confirmation
- 📥 **PDF Export** - Generate downloadable invoice PDFs
- 💾 **SQLite Database** - Persistent local storage
- 🔍 **Search & Filter** - Find invoices quickly
- 📊 **Analytics Dashboard** - Visual insights into billing

### Invoice Features
- Multiple line items per invoice
- Automatic total calculation
- Tax rate configuration
- Invoice status tracking (Paid, Pending, Overdue)
- Client information management
- Custom notes and terms
- Unique invoice numbering

### Analytics
- Monthly revenue tracking
- Status distribution
- Top clients by revenue
- Cumulative revenue trends
- Payment rate calculations
- Upcoming due dates

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Create project directory**
```bash
mkdir invoice-system
cd invoice-system
```

2. **Create and save files**
   - Save `app.py` (main application)
   - Save `requirements.txt` (dependencies)
   - Save `README.md` (this file)

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📖 Usage Guide

### Creating Your First Invoice

1. **Navigate to "Create Invoice"** in the sidebar
2. **Fill in client information**:
   - Client Name (required)
   - Client Email (required)
   - Client Address (optional)
3. **Set invoice details**:
   - Issue Date
   - Due Date
   - Status (pending/paid/overdue)
   - Tax Rate
4. **Add line items**:
   - Description
   - Quantity
   - Rate per unit
   - Click "➕ Add Item" for more items
5. **Add notes** (optional)
6. **Click "✅ Create Invoice"**

### Managing Invoices

**View All Invoices**:
- Go to "View Invoices" in sidebar
- Use search bar to find specific invoices
- Filter by status
- Sort by date or amount

**Edit Invoice**:
- Click "✏️ Edit" button on any invoice
- Modify details as needed
- Click "💾 Save Invoice"

**Delete Invoice**:
- Click "🗑️ Delete" button
- Confirm deletion

**Download PDF**:
- Click "📥 Download PDF"
- Click "💾 Save PDF" to download

### Using the Dashboard

The dashboard provides:
- **KPI Cards**: Total revenue, paid, pending, and overdue amounts
- **Recent Invoices**: Latest 5 invoices
- **Quick Stats**: Average invoice value and payment rate
- **Upcoming Due Dates**: Next 3 invoices due

### Analytics

Navigate to "Analytics" to view:
- **Monthly Revenue Chart**: Bar chart showing revenue trends
- **Status Distribution**: Pie chart of invoice statuses
- **Top 10 Clients**: Horizontal bar chart of best clients
- **Cumulative Revenue**: Line chart showing total revenue over time

## 📊 Database Structure

### Invoices Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| invoice_number | TEXT | Unique invoice identifier |
| client_name | TEXT | Client's full name |
| client_email | TEXT | Client's email address |
| client_address | TEXT | Client's mailing address |
| issue_date | TEXT | Date invoice was created |
| due_date | TEXT | Payment due date |
| items | TEXT | JSON array of line items |
| subtotal | REAL | Total before tax |
| tax_rate | REAL | Tax percentage |
| tax_amount | REAL | Calculated tax amount |
| total | REAL | Final total amount |
| status | TEXT | paid/pending/overdue |
| notes | TEXT | Additional notes |
| created_at | TEXT | Timestamp of creation |
| updated_at | TEXT | Last update timestamp |

### Line Items Structure (JSON)

```json
[
  {
    "description": "Web Development Services",
    "quantity": 40,
    "rate": 150.00
  },
  {
    "description": "UI/UX Design",
    "quantity": 20,
    "rate": 120.00
  }
]
```

## 🎨 Customization

### Company Information

Edit the `show_settings()` function in `app.py`:

```python
def show_settings():
    company_name = st.text_input("Company Name", value="Your Company Name")
    company_address = st.text_area("Company Address", value="Your Address")
    company_email = st.text_input("Company Email", value="your@email.com")
    company_phone = st.text_input("Company Phone", value="Your Phone")
```

### Invoice Number Format

Modify `generate_invoice_number()`:

```python
def generate_invoice_number():
    # Format: INV-YYYYMM-0001
    return f"INV-{datetime.now().strftime('%Y%m')}-{str(count + 1).zfill(4)}"
```

### Default Tax Rate

Change in the form:

```python
tax_rate = st.number_input("Tax Rate (%)", value=10.0)  # Change 10.0 to your rate
```

### Status Options

Modify status choices:

```python
status = st.selectbox("Status", ["draft", "sent", "paid", "cancelled"])
```

## 💡 Use Cases

### Freelancers
- Track client billings
- Monitor payment status
- Generate professional invoices
- Analyze income streams

### Small Businesses
- Manage accounts receivable
- Track customer payments
- Generate financial reports
- Monitor cash flow

### Consultants
- Bill hourly work
- Track project invoices
- Client revenue analysis
- Payment reminders

### Service Providers
- Recurring billing
- Service tracking
- Client management
- Revenue forecasting

## 🔧 Technical Details

### Technology Stack
- **Frontend**: Streamlit 1.29.0
- **Database**: SQLite3 (built-in)
- **Data Processing**: Pandas 2.1.4
- **Visualizations**: Plotly 5.18.0
- **Date Handling**: python-dateutil 2.8.2

### File Structure
```
invoice-system/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── invoices.db        # SQLite database (created on first run)
└── .streamlit/        # Streamlit config (optional)
    └── config.toml
```

### Performance
- **Load Time**: <2 seconds
- **Database Queries**: Optimized with indexes
- **Memory Usage**: ~50 MB
- **Concurrent Users**: 1 (local), scalable for multi-user

## 📥 Data Import/Export

### Export Invoice Data

All invoices can be exported via the database:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('invoices.db')
df = pd.read_sql_query("SELECT * FROM invoices", conn)
df.to_csv('invoices_export.csv', index=False)
```

### Backup Database

```bash
# Create backup
cp invoices.db invoices_backup_$(date +%Y%m%d).db

# Restore from backup
cp invoices_backup_20251015.db invoices.db
```

## 🐛 Troubleshooting

### Database Issues

**Issue**: Database locked error
```bash
Solution: Close all connections and restart the application
```

**Issue**: Data not persisting
```bash
Solution: Check write permissions in the directory
chmod 644 invoices.db
```

### PDF Generation

**Issue**: PDF not downloading
```bash
Solution: Check browser download settings and allow popups
```

### Performance Issues

**Issue**: Slow loading with many invoices
```bash
Solution: Add pagination or limit displayed results
```

## 🚀 Advanced Features (Future)

### Planned Enhancements
- [ ] Email invoice sending
- [ ] Payment gateway integration
- [ ] Recurring invoices
- [ ] Multi-currency support
- [ ] Client portal
- [ ] Expense tracking
- [ ] Receipt uploads
- [ ] Automated reminders
- [ ] Custom templates
- [ ] Multi-user access
- [ ] Mobile app

## 🔐 Security Best Practices

### For Production Use

1. **Authentication**: Add user login
2. **HTTPS**: Use SSL certificates
3. **Backup**: Regular database backups
4. **Validation**: Input sanitization
5. **Access Control**: Role-based permissions

### Data Protection

```python
# Example: Add password protection
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show app
    main()
```

## 📊 Sample Invoice

```
╔════════════════════════════════════════════════════╗
║                    INVOICE                          ║
╠════════════════════════════════════════════════════╣

Invoice Number: INV-202510-0001
Issue Date:     2025-10-15
Due Date:       2025-11-15
Status:         PENDING

FROM:
Your Company Name
123 Business Street
City, State, ZIP

BILL TO:
Acme Corporation
billing@acme.com
456 Client Avenue

────────────────────────────────────────────────────
ITEMS
────────────────────────────────────────────────────
Web Development        40 x $150.00 = $6,000.00
UI/UX Design          20 x $120.00 = $2,400.00
────────────────────────────────────────────────────

                              Subtotal: $8,400.00
                          Tax (10.0%): $  840.00
                                TOTAL: $9,240.00

────────────────────────────────────────────────────
Thank you for your business!
╚════════════════════════════════════════════════════╝
```

## 📞 Support

### Getting Help

**Issues**: Check troubleshooting section  
**Questions**: Email maqbuul@outlook.com  
**Bugs**: Report via GitHub issues  
**Features**: Submit feature requests

### Contact Information

**Developer**: Abdiwahid Hussein Ali  
**Email**: maqbuul@outlook.com  
**Phone**: +254 471 777 2131  
**Location**: Nairobi, Kenya

## 📝 License

MIT License

Copyright (c) 2025 Abdiwahid Hussein Ali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

## 🙏 Acknowledgments

- Streamlit team for the framework
- SQLite for the database engine
- Plotly for visualizations
- Open-source community

## 🌟 Show Your Support

If you find this useful:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 📢 Share with others

---

**Built with ❤️ for accounting professionals and small business owners**

Last Updated: October 2025