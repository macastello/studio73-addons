# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    edicom_ean13 = fields.Char(string="EAN13")
    eci_buyer_code = fields.Char(
        string="Código corto comprador",
        help="""A la bajada de pedidos ECI se concatenará este valor
        con el código del pedido""",
    )
    edicom_export_invoice_path = fields.Char(
        string="Ruta exportación facturas",
        help="Ruta donde se exportarán los ficheros de las facturas",
        default="./PRODUCCION/SALIDA/",
        tracking=True,
    )
