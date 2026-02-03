# Copyright 2021 Studio73 - Iván Pérez <ivan.perez@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    _order = "qty asc, name asc"

    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot")

    @api.constrains("purchase")
    def _check_purchase_packagings(self):
        for packaging in self:
            packagings = packaging.search(
                [
                    ("package_type_id", "=", packaging.package_type_id.id),
                    "|",
                    "&",
                    ("product_id", "!=", False),
                    ("product_id", "=", packaging.product_id.id),
                    "&",
                    ("lot_id", "!=", False),
                    ("lot_id", "=", packaging.lot_id.id),
                    ("purchase", "=", True),
                ]
            )
            if len(packagings) > 1:
                raise UserError(
                    _(
                        "For each product, only one purchase packaging per "
                        "packaging type can be configured"
                    )
                )

    @api.constrains("sales")
    def _check_sales_packagings(self):
        for packaging in self:
            if packaging.sales:
                packagings = packaging.search(
                    [
                        ("package_type_id", "=", packaging.package_type_id.id),
                        "|",
                        "&",
                        ("product_id", "!=", False),
                        ("product_id", "=", packaging.product_id.id),
                        "&",
                        ("lot_id", "!=", False),
                        ("lot_id", "=", packaging.lot_id.id),
                        ("id", "!=", packaging.id),
                        ("sales", "=", True),
                    ]
                )
                if len(packagings) > 1:
                    raise UserError(
                        _(
                            "For each product, only one sales packaging per "
                            "packaging type can be configured"
                        )
                    )
