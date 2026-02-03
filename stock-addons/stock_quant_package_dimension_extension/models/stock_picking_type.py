# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    hide_delivery_package_wizard = fields.Boolean(
        string="Ocultar ventana emergente de paquetes",
        help="Marcar este campo hará que no se muestre la ventana emergente para"
        " seleccionar el tipo de paquete al poner mercancía en paquete.",
    )
