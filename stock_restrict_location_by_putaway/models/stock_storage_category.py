# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockStorageCategory(models.Model):
    _inherit = "stock.storage.category"

    max_volume = fields.Float(
        string="Volumen máximo",
        help="Volumen máximo que puede almacenar esta categoría de almacenamiento. Si "
        "no se especifica, no hay límite.",
        digits="Volume",
    )
    volume_uom_name = fields.Char(
        string="Volume unit", compute="_compute_volume_uom_name"
    )

    _sql_constraints = [
        (
            "positive_max_volume",
            "CHECK(max_volume >= 0)",
            "Max volume should be a positive number.",
        ),
    ]

    def _compute_volume_uom_name(self):
        self.volume_uom_name = self.env[
            "product.template"
        ]._get_volume_uom_name_from_ir_config_parameter()
