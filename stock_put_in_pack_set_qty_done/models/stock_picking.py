# Copyright 2024 Studio73 - Roger Amorós <roger@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _package_move_lines(self, batch_pack=False):
        res = super()._package_move_lines(batch_pack=batch_pack)
        if not res or self.picking_type_id.assign_qty_at_put_in_pack:
            return res
        if not any(r.picked for r in res):
            raise UserError(
                _("Debe asignar cantidades hechas antes de poner en paquete.")
            )
        return res
