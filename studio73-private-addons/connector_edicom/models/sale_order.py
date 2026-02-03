# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    edicom_order_id = fields.Integer(string="ID EDI", copy=False)
    edicom_node = fields.Char(
        string="Tipo de pedido",
        copy=False,
    )
    edicom_dept = fields.Char(
        string="Departamento",
        copy=False,
    )
    edicom_function = fields.Char(
        string="Función del pedido",
        copy=False,
    )
    edicom_special_cond = fields.Char(
        string="Condiciones especiales de envío",
        copy=False,
    )
    edicom_emitter_id = fields.Many2one(
        string="Emisor del mensaje",
        comodel_name="res.partner",
        copy=False,
    )
    edicom_buyer_id = fields.Many2one(
        string="Comprador",
        comodel_name="res.partner",
        copy=False,
    )
    edicom_original_order = fields.Char(string="Código EDI original", copy=False)
