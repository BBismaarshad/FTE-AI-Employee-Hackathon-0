"""
Odoo MCP Server - Gold Tier AI Employee Skill

Integration with Odoo Community Edition for accounting and business management.

Provides tools for:
- Creating and managing invoices
- Managing partners (customers/suppliers)
- Creating payments
- Checking account balances
- Generating financial reports

Uses Odoo JSON-RPC API (Odoo 19+).
Part of the Gold Tier requirements for the FTE AI Employee Hackathon.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import xmlrpc.client
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class OdooMCP:
    """MCP server for Odoo operations via JSON-RPC API."""

    def __init__(self, url, db, username, password, vault_path=None, dry_run=False):
        """
        Initialize Odoo MCP Server.

        Args:
            url: Odoo server URL (e.g., http://localhost:8069)
            db: Database name
            username: Odoo username
            password: Odoo password
            vault_path: Path to Obsidian vault for logging
            dry_run: If True, simulate operations without connecting to Odoo
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.dry_run = dry_run
        self.uid = None
        self.models = None
        self.logger = logging.getLogger('OdooMCP')

        # Vault setup for logging
        if vault_path:
            self.vault_path = Path(vault_path)
            self.logs_folder = self.vault_path / 'Logs'
            self.logs_folder.mkdir(parents=True, exist_ok=True)
        else:
            self.vault_path = None
            self.logs_folder = None

        # Authenticate if not in dry run mode
        if not dry_run:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Odoo server."""
        try:
            self.logger.info(f"Connecting to Odoo at {self.url}...")
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Get server version
            version_info = common.version()
            self.logger.info(f"Odoo version: {version_info.get('server_version', 'unknown')}")

            # Authenticate
            self.uid = common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                raise Exception("Authentication failed - check credentials")

            # Setup models proxy
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            self.logger.info(f"✅ Authenticated with Odoo, UID: {self.uid}")

        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Odoo: {e}")
            if not self.dry_run:
                raise

    def _execute(self, model: str, method: str, args: List, kwargs: Dict = None) -> Any:
        """
        Execute an Odoo model method.

        Args:
            model: Odoo model name (e.g., 'res.partner')
            method: Method name (e.g., 'search_read')
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Result from Odoo
        """
        if kwargs is None:
            kwargs = {}

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )

    def list_partners(self, limit: int = 10, customer_only: bool = True) -> Dict:
        """
        List Odoo partners (customers/suppliers).

        Args:
            limit: Maximum number of partners to return
            customer_only: If True, only return customers

        Returns:
            dict with success status and partner list
        """
        if self.dry_run:
            return {
                "success": True,
                "partners": [
                    {"id": 1, "name": "Sample Customer A", "email": "customer.a@example.com"},
                    {"id": 2, "name": "Sample Customer B", "email": "customer.b@example.com"}
                ],
                "count": 2,
                "dry_run": True
            }

        try:
            # Build domain filter
            domain = [['customer_rank', '>', 0]] if customer_only else []

            # Search and read partners
            partners = self._execute(
                'res.partner', 'search_read',
                [domain],
                {'fields': ['name', 'email', 'phone', 'customer_rank', 'supplier_rank'], 'limit': limit}
            )

            self.logger.info(f"Retrieved {len(partners)} partners")
            self._log_action('list_partners', {'count': len(partners), 'status': 'success'})

            return {
                "success": True,
                "partners": partners,
                "count": len(partners)
            }

        except Exception as e:
            self.logger.error(f"Failed to list partners: {e}")
            return {"success": False, "error": str(e)}

    def create_invoice(self, partner_id: int, amount: float, description: str = "AI Employee Services",
                      product_name: str = "Service", require_approval: bool = True) -> Dict:
        """
        Create a draft invoice in Odoo.

        Args:
            partner_id: Odoo partner ID
            amount: Invoice amount
            description: Line item description
            product_name: Product/service name
            require_approval: If True, create as draft requiring approval

        Returns:
            dict with success status and invoice details
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create invoice for partner {partner_id} for ${amount}")
            return {
                "success": True,
                "invoice_id": 999,
                "invoice_number": "INV/2026/0999",
                "amount": amount,
                "status": "draft",
                "dry_run": True
            }

        try:
            # Create invoice
            invoice_vals = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # Customer invoice
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': description,
                        'quantity': 1,
                        'price_unit': amount,
                    })
                ],
            }

            invoice_id = self._execute('account.move', 'create', [invoice_vals])

            # Get invoice details
            invoice = self._execute(
                'account.move', 'read',
                [invoice_id],
                {'fields': ['name', 'amount_total', 'state', 'partner_id']}
            )[0]

            self.logger.info(f"✅ Created invoice {invoice['name']} for ${amount}")
            self._log_action('create_invoice', {
                'invoice_id': invoice_id,
                'invoice_number': invoice['name'],
                'amount': amount,
                'partner_id': partner_id,
                'status': 'success'
            })

            return {
                "success": True,
                "invoice_id": invoice_id,
                "invoice_number": invoice['name'],
                "amount": invoice['amount_total'],
                "status": invoice['state'],
                "partner": invoice['partner_id'][1] if invoice['partner_id'] else None
            }

        except Exception as e:
            self.logger.error(f"Failed to create invoice: {e}")
            return {"success": False, "error": str(e)}

    def post_invoice(self, invoice_id: int) -> Dict:
        """
        Post (validate) a draft invoice.

        Args:
            invoice_id: Odoo invoice ID

        Returns:
            dict with success status
        """
        if self.dry_run:
            return {"success": True, "invoice_id": invoice_id, "status": "posted", "dry_run": True}

        try:
            # Post the invoice
            self._execute('account.move', 'action_post', [[invoice_id]])

            self.logger.info(f"✅ Posted invoice {invoice_id}")
            self._log_action('post_invoice', {'invoice_id': invoice_id, 'status': 'success'})

            return {"success": True, "invoice_id": invoice_id, "status": "posted"}

        except Exception as e:
            self.logger.error(f"Failed to post invoice: {e}")
            return {"success": False, "error": str(e)}

    def create_payment(self, partner_id: int, amount: float, payment_type: str = 'inbound',
                      reference: str = None) -> Dict:
        """
        Create a payment record.

        Args:
            partner_id: Odoo partner ID
            amount: Payment amount
            payment_type: 'inbound' (receive) or 'outbound' (send)
            reference: Payment reference/memo

        Returns:
            dict with success status and payment details
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would create {payment_type} payment of ${amount}")
            return {
                "success": True,
                "payment_id": 888,
                "amount": amount,
                "type": payment_type,
                "dry_run": True
            }

        try:
            payment_vals = {
                'partner_id': partner_id,
                'amount': amount,
                'payment_type': payment_type,
                'partner_type': 'customer' if payment_type == 'inbound' else 'supplier',
                'date': datetime.now().strftime('%Y-%m-%d'),
            }

            if reference:
                payment_vals['ref'] = reference

            payment_id = self._execute('account.payment', 'create', [payment_vals])

            self.logger.info(f"✅ Created {payment_type} payment of ${amount}")
            self._log_action('create_payment', {
                'payment_id': payment_id,
                'amount': amount,
                'type': payment_type,
                'status': 'success'
            })

            return {
                "success": True,
                "payment_id": payment_id,
                "amount": amount,
                "type": payment_type
            }

        except Exception as e:
            self.logger.error(f"Failed to create payment: {e}")
            return {"success": False, "error": str(e)}

    def get_account_summary(self) -> Dict:
        """
        Get a summary of account balances.

        Returns:
            dict with receivables, payables, and net balance
        """
        if self.dry_run:
            return {
                "success": True,
                "total_receivable": 5000.0,
                "total_payable": 1200.0,
                "net_balance": 3800.0,
                "currency": "USD",
                "dry_run": True
            }

        try:
            # Get receivable account balance
            receivable_domain = [
                ['account_type', '=', 'asset_receivable'],
                ['reconciled', '=', False]
            ]

            receivable_lines = self._execute(
                'account.move.line', 'search_read',
                [receivable_domain],
                {'fields': ['debit', 'credit']}
            )

            total_receivable = sum(line['debit'] - line['credit'] for line in receivable_lines)

            # Get payable account balance
            payable_domain = [
                ['account_type', '=', 'liability_payable'],
                ['reconciled', '=', False]
            ]

            payable_lines = self._execute(
                'account.move.line', 'search_read',
                [payable_domain],
                {'fields': ['debit', 'credit']}
            )

            total_payable = sum(line['credit'] - line['debit'] for line in payable_lines)

            net_balance = total_receivable - total_payable

            self.logger.info(f"Account summary: Receivable=${total_receivable:.2f}, Payable=${total_payable:.2f}")

            return {
                "success": True,
                "total_receivable": round(total_receivable, 2),
                "total_payable": round(total_payable, 2),
                "net_balance": round(net_balance, 2),
                "currency": "USD"
            }

        except Exception as e:
            self.logger.error(f"Failed to get account summary: {e}")
            return {"success": False, "error": str(e)}

    def get_recent_invoices(self, limit: int = 10, state: str = None) -> Dict:
        """
        Get recent invoices.

        Args:
            limit: Maximum number of invoices to return
            state: Filter by state ('draft', 'posted', 'cancel')

        Returns:
            dict with invoice list
        """
        if self.dry_run:
            return {
                "success": True,
                "invoices": [
                    {"id": 1, "name": "INV/2026/0001", "amount": 1500.0, "state": "posted"},
                    {"id": 2, "name": "INV/2026/0002", "amount": 2000.0, "state": "draft"}
                ],
                "count": 2,
                "dry_run": True
            }

        try:
            domain = [['move_type', '=', 'out_invoice']]
            if state:
                domain.append(['state', '=', state])

            invoices = self._execute(
                'account.move', 'search_read',
                [domain],
                {
                    'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date'],
                    'limit': limit,
                    'order': 'invoice_date desc'
                }
            )

            return {
                "success": True,
                "invoices": invoices,
                "count": len(invoices)
            }

        except Exception as e:
            self.logger.error(f"Failed to get invoices: {e}")
            return {"success": False, "error": str(e)}

    def _log_action(self, action_type: str, details: Dict):
        """Log action to daily log file."""
        if not self.logs_folder:
            return

        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": "odoo_mcp",
            **details
        }

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                logs = []

        # Append new entry
        logs.append(entry)

        # Write back
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def main():
    """CLI interface for Odoo MCP Server."""
    parser = argparse.ArgumentParser(description='Odoo MCP Server - Gold Tier AI Employee')
    parser.add_argument('--url', type=str, default='http://localhost:8069', help='Odoo URL')
    parser.add_argument('--db', type=str, default='odoo', help='Odoo Database')
    parser.add_argument('--username', type=str, default='admin', help='Odoo Username')
    parser.add_argument('--password', type=str, help='Odoo Password (or set ODOO_PASSWORD env var)')
    parser.add_argument('--vault', type=str, help='Path to Obsidian vault for logging')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    # Get password from env if not provided
    password = args.password or os.getenv('ODOO_PASSWORD', 'admin')

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        odoo = OdooMCP(
            url=args.url,
            db=args.db,
            username=args.username,
            password=password,
            vault_path=args.vault,
            dry_run=args.dry_run
        )

        print("\n🔧 Odoo MCP Server Ready")
        print("=" * 50)
        print("Available commands:")
        print("  partners          - List partners")
        print("  invoices          - List recent invoices")
        print("  invoice <id> <amt> - Create invoice")
        print("  post <id>         - Post invoice")
        print("  payment <id> <amt> - Create payment")
        print("  summary           - Account summary")
        print("  exit              - Exit")
        print("=" * 50)

        # Interactive CLI
        while True:
            try:
                cmd = input("\nodoo> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == 'partners':
                    result = odoo.list_partners()
                    print(json.dumps(result, indent=2))

                elif cmd[0] == 'invoices':
                    result = odoo.get_recent_invoices()
                    print(json.dumps(result, indent=2))

                elif cmd[0] == 'invoice':
                    if len(cmd) >= 3:
                        result = odoo.create_invoice(int(cmd[1]), float(cmd[2]))
                        print(json.dumps(result, indent=2))
                    else:
                        print("Usage: invoice <partner_id> <amount>")

                elif cmd[0] == 'post':
                    if len(cmd) >= 2:
                        result = odoo.post_invoice(int(cmd[1]))
                        print(json.dumps(result, indent=2))
                    else:
                        print("Usage: post <invoice_id>")

                elif cmd[0] == 'payment':
                    if len(cmd) >= 3:
                        result = odoo.create_payment(int(cmd[1]), float(cmd[2]))
                        print(json.dumps(result, indent=2))
                    else:
                        print("Usage: payment <partner_id> <amount>")

                elif cmd[0] == 'summary':
                    result = odoo.get_account_summary()
                    print(json.dumps(result, indent=2))

                elif cmd[0] == 'exit':
                    print("👋 Goodbye!")
                    break

                else:
                    print(f"Unknown command: {cmd[0]}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Failed to initialize Odoo MCP: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
