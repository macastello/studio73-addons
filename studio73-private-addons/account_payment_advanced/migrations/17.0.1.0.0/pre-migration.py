# Copyright 2024 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tools.sql import column_exists, create_column


def migrate(cr, version):
    if column_exists(cr, "account_payment_entry", "type"):
        if not column_exists(cr, "account_payment_entry", "entry_type"):
            create_column(cr, "account_payment_entry", "entry_type", "VARCHAR(255)")
        cr.execute("UPDATE account_payment_entry SET entry_type = type")
