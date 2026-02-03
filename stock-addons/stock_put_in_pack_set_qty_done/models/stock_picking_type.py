# Copyright 2024 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    assign_qty_at_put_in_pack = fields.Boolean(
        string="Asignar cantidades al poner en paquete",
        help="Marcando este check se asignarán las cantidades al poner en paquete de "
        "todas las líneas del albarán. Si no se marca, no se asignarán las cantidades "
        "automáticamente y en caso de no haber cantidades hechas saltará un aviso.",
        default=True,
    )
