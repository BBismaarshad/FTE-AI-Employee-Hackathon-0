# Odoo MCP Server - Agent Skill

**Tier:** Gold  
**Category:** Accounting & Business Management  
**Status:** ✅ Ready

## Overview

Integration with Odoo Community Edition (v19+) for accounting and business management. Provides AI Employee with access to invoicing, partner management, payments, and financial reporting through Odoo's JSON-RPC API.

## Features

- 📋 **Invoice Management** - Create, post, and track invoices
- 👥 **Partner Management** - Manage customers and suppliers
- 💰 **Payment Processing** - Record payments and receipts
- 📊 **Account Summaries** - Real-time financial metrics
- 🔍 **Financial Reports** - Receivables, payables, balances
- 📝 **Audit Logging** - All operations logged to vault

## Prerequisites

### 1. Odoo Installation

**Option A: Docker (Recommended)**

```bash
# Start Odoo with Docker Compose
cd docker/odoo
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f odoo
```

**Option B: Manual Installation**

See [Odoo Documentation](https://www.odoo.com/documentation/19.0/administration/install.html)

### 2. Python Dependencies

```bash
# Already included in requirements.txt
pip install xmlrpc
```

### 3. Odoo Setup

1. Access Odoo: http://localhost:8069
2. Create database: `odoo`
3. Set admin password
4. Install Accounting module

## Installation

### Verify Installation

```bash
python skills/odoo_mcp.py --help
```

### Test Connection

```bash
# Dry run mode (no Odoo required)
python skills/odoo_mcp.py --dry-run

# Connect to Odoo
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password admin
```

## Usage

### Interactive CLI

```bash
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password yourpassword

# Available commands:
odoo> partners          # List customers
odoo> invoices          # List recent invoices
odoo> invoice 1 1500    # Create invoice for partner 1, amount $1500
odoo> post 5            # Post (validate) invoice #5
odoo> payment 1 1500    # Record payment from partner 1
odoo> summary           # Get account summary
odoo> exit              # Exit
```

### Programmatic Usage

```python
from skills.odoo_mcp import OdooMCP

# Initialize
odoo = OdooMCP(
    url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='admin',
    vault_path='./AI_Employee_Vault'
)

# List partners
partners = odoo.list_partners(limit=10)
print(partners)

# Create invoice
invoice = odoo.create_invoice(
    partner_id=1,
    amount=1500.00,
    description="AI Employee Services - May 2026"
)
print(f"Invoice created: {invoice['invoice_number']}")

# Get account summary
summary = odoo.get_account_summary()
print(f"Receivable: ${summary['total_receivable']}")
print(f"Payable: ${summary['total_payable']}")
```

## API Methods

### list_partners(limit=10, customer_only=True)

List Odoo partners (customers/suppliers).

**Returns:**
```json
{
  "success": true,
  "partners": [
    {
      "id": 1,
      "name": "Customer A",
      "email": "customer.a@example.com",
      "phone": "+1234567890"
    }
  ],
  "count": 1
}
```

### create_invoice(partner_id, amount, description)

Create a draft invoice.

**Parameters:**
- `partner_id` (int): Odoo partner ID
- `amount` (float): Invoice amount
- `description` (str): Line item description

**Returns:**
```json
{
  "success": true,
  "invoice_id": 5,
  "invoice_number": "INV/2026/0005",
  "amount": 1500.0,
  "status": "draft"
}
```

### post_invoice(invoice_id)

Post (validate) a draft invoice.

**Returns:**
```json
{
  "success": true,
  "invoice_id": 5,
  "status": "posted"
}
```

### create_payment(partner_id, amount, payment_type='inbound')

Record a payment.

**Parameters:**
- `partner_id` (int): Odoo partner ID
- `amount` (float): Payment amount
- `payment_type` (str): 'inbound' (receive) or 'outbound' (send)

**Returns:**
```json
{
  "success": true,
  "payment_id": 10,
  "amount": 1500.0,
  "type": "inbound"
}
```

### get_account_summary()

Get account balances summary.

**Returns:**
```json
{
  "success": true,
  "total_receivable": 5000.0,
  "total_payable": 1200.0,
  "net_balance": 3800.0,
  "currency": "USD"
}
```

### get_recent_invoices(limit=10, state=None)

Get recent invoices.

**Parameters:**
- `limit` (int): Maximum invoices to return
- `state` (str): Filter by state ('draft', 'posted', 'cancel')

**Returns:**
```json
{
  "success": true,
  "invoices": [
    {
      "id": 5,
      "name": "INV/2026/0005",
      "amount_total": 1500.0,
      "state": "posted",
      "invoice_date": "2026-05-01"
    }
  ],
  "count": 1
}
```

## Configuration

### Environment Variables

```bash
# Set Odoo password via environment variable
export ODOO_PASSWORD=your_secure_password

# Use in command
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin
```

### Vault Integration

```bash
# Enable logging to vault
python skills/odoo_mcp.py --vault .\AI_Employee_Vault --url http://localhost:8069 --db odoo --username admin --password admin
```

All operations will be logged to `Logs/YYYY-MM-DD.json`.

## Docker Setup

### Start Odoo

```bash
cd docker/odoo
docker compose up -d
```

### Access Odoo

1. Open browser: http://localhost:8069
2. Create database: `odoo`
3. Set master password
4. Login as admin

### Install Accounting Module

1. Go to Apps
2. Search "Accounting"
3. Click Install
4. Wait for installation

### Create Test Data

```bash
# Use Odoo CLI to create test partners
python skills/odoo_mcp.py --url http://localhost:8069 --db odoo --username admin --password admin

odoo> partners
# Should show default partners
```

## Integration with Weekly Audit

The Weekly Audit skill automatically uses Odoo data when available:

```bash
python skills/weekly_audit.py --vault .\AI_Employee_Vault --odoo-url http://localhost:8069 --odoo-db odoo --odoo-user admin --odoo-password admin
```

This provides:
- Real-time revenue tracking
- Accounts receivable/payable
- Invoice status
- Financial metrics for CEO Briefing

## Security Best Practices

### 1. Secure Credentials

```bash
# Never hardcode passwords
# Use environment variables
export ODOO_PASSWORD=secure_password

# Or use .env file (add to .gitignore)
echo "ODOO_PASSWORD=secure_password" >> .env
```

### 2. Network Security

```bash
# For production, use HTTPS
--url https://odoo.yourdomain.com

# Restrict Docker ports
# Edit docker-compose.yml to bind to localhost only
ports:
  - "127.0.0.1:8069:8069"
```

### 3. Database Backups

```bash
# Backups are automatic with Docker setup
# Check backups folder
ls docker/odoo/backups/

# Manual backup
docker compose exec odoo-db pg_dump -U odoo odoo > backup.sql
```

## Troubleshooting

### Issue: "Authentication failed"

**Solution:**
1. Verify Odoo is running: http://localhost:8069
2. Check database name: `--db odoo`
3. Verify credentials
4. Check Odoo logs: `docker compose logs odoo`

### Issue: "Connection refused"

**Solution:**
1. Start Odoo: `docker compose up -d`
2. Wait for startup: `docker compose logs -f odoo`
3. Check port: `docker compose ps`

### Issue: "Module not found: xmlrpc"

**Solution:**
```bash
pip install xmlrpc
# Or reinstall requirements
pip install -r requirements.txt
```

### Issue: "Invoice creation failed"

**Cause:** Accounting module not installed

**Solution:**
1. Login to Odoo web interface
2. Go to Apps
3. Install "Accounting" module
4. Retry invoice creation

## Advanced Usage

### Custom Invoice Lines

Modify `create_invoice()` to add multiple line items:

```python
invoice_vals = {
    'partner_id': partner_id,
    'move_type': 'out_invoice',
    'invoice_line_ids': [
        (0, 0, {'name': 'Service A', 'quantity': 1, 'price_unit': 1000}),
        (0, 0, {'name': 'Service B', 'quantity': 2, 'price_unit': 250}),
    ],
}
```

### Batch Operations

```python
# Create multiple invoices
partners = odoo.list_partners(limit=10)
for partner in partners['partners']:
    odoo.create_invoice(partner['id'], 1500, "Monthly Service")
```

### Financial Reports

```python
# Get detailed financial data
summary = odoo.get_account_summary()
invoices = odoo.get_recent_invoices(limit=50, state='posted')

# Calculate metrics
total_revenue = sum(inv['amount_total'] for inv in invoices['invoices'])
avg_invoice = total_revenue / len(invoices['invoices'])
```

## Odoo API Reference

- [Odoo External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo Models](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Accounting Module](https://www.odoo.com/documentation/19.0/applications/finance/accounting.html)

## Related Skills

- **Weekly Audit** - Uses Odoo data for CEO Briefing
- **Email MCP Server** - Send invoice notifications
- **Ralph Loop** - Automate multi-step accounting tasks

## Support

- 📚 **Documentation:** This file + Odoo docs
- 🐛 **Issues:** Check Docker logs and Odoo logs
- 💬 **Community:** Wednesday Research Meetings

---

**Built for Gold Tier - FTE AI Employee Hackathon**  
**Provides autonomous accounting and business management**
