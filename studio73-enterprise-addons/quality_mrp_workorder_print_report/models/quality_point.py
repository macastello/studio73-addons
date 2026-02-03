# Copyright 2024 Studio73 - Alex Garcia - <alex@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QualityPoint(models.Model):
    _inherit = "quality.point"

    report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Informe",
        domain=[
            "|",
            "|",
            ("model", "=", "stock.lot"),
            ("model", "=", "product.product"),
            ("model", "=", "mrp.workorder"),
        ],
    )
    report_model = fields.Selection(
        string="Modelo informe",
        selection=[
            ("product.product", "Variante de producto"),
            ("stock.lot", "Lote"),
            ("mrp.workorder", "Orden de trabajo"),
        ],
        help="Este campo se utiliza para definir de "
        "que modelo viene el informe que quiere imprimir.",
    )

    copies_number = fields.Integer(
        "Número de copias",
        default=1,
        help=(
            "El valor introducido aquí servirá para imprimir múltiples etiquetas,"
            " de forma que si se están fabricando 4 unidades de un producto y aquí "
            "tenemos valor 2, en total se imprimirán un total de 8 etiquetas"
        ),
    )

    @api.constrains("copies_number")
    def _check_copies_number(self):
        for record in self:
            if record.copies_number <= 0:
                raise ValidationError(
                    _("El número de copias debe ser igual o mayor a 1")
                )
