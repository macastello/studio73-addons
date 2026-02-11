# Copyright 2025 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "edicom.export.mixin"]

    def action_export_edicom(self):
        export_config = self.env.ref("connector_edicom.edicom_export_picking_data")
        self.export_to_edicom(
            self,
            export_config,
            export_path=self.partner_id.edicom_export_picking_path
            or self.partner_id.commercial_partner_id.edicom_export_picking_path,
        )
        return True
