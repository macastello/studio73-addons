# Copyright 2023 Studio73 - Guillermo Llinares - <guillermo@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    print_as_zpl = fields.Boolean(
        string="Print as ZPL",
        help="If the report of Type Text is a ZPL label, this checkbox needs to be "
        "checked to print it correctly. Otherwise it will print the actual ZPL "
        "code on the label.",
    )
