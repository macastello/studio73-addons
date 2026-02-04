# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        for move_line in self:
            if (
                not move_line.location_dest_id.storage_category_id
                or not move_line.picking_id.picking_type_id.restrict_location_by_putaway
            ):
                continue
            package = move_line.result_package_id
            if package and package.package_type_id:
                quant_data = self.env["stock.quant"].search(
                    [
                        ("package_id.package_type_id", "=", package.package_type_id.id),
                        ("location_id", "child_of", move_line.location_dest_id.id),
                    ]
                )
                location_qty = len(quant_data.package_id)
            else:
                quant_data = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", move_line.product_id.id),
                        ("location_id", "child_of", move_line.location_dest_id.id),
                    ]
                )
                location_qty = sum(q.quantity for q in quant_data)
            if move_line.location_dest_id._check_can_be_used(
                move_line.product_id,
                quantity=move_line.quantity,
                package=package,
                location_qty=location_qty,
            ):
                continue
            # Esto "duplica" la función de Odoo pero solo se hace en el caso de tener
            # que mostrar mensaje
            error_msg = move_line.location_dest_id._storage_category_reason(
                move_line.product_id,
                quantity=move_line.quantity,
                package=package,
                location_qty=location_qty,
            )
            if error_msg == "weight":
                raise UserError(
                    _(
                        "No puedes mover el producto "
                        f"{move_line.product_id.display_name} a la ubicación "
                        f"{move_line.location_dest_id.name} porque excede el límite de "
                        "peso. Si crees que es un error, revisa el contenido de esta "
                        "ubicación y ajusta el inventario para poder mover el producto."
                    )
                )
            elif error_msg == "capacity":
                raise UserError(
                    _(
                        "No puede mover el producto "
                        f"{move_line.product_id.display_name} a la ubicación "
                        f"{move_line.location_dest_id.name} porque excede su capacidad "
                        "máxima. Si crees que es un error, revisa el contenido de esta "
                        "ubicación y ajusta el inventario para poder mover el producto."
                    )
                )
            elif error_msg == "product":
                raise UserError(
                    _(
                        "No puede mover el producto "
                        f"{move_line.product_id.display_name} a la ubicación "
                        f"{move_line.location_dest_id.name} porque ya contiene otro "
                        "producto. Si crees que es un error, revisa el contenido de "
                        "esta ubicación y ajusta el inventario para poder mover el "
                        "producto."
                    )
                )
            else:
                raise UserError(
                    _(
                        "No puedes mover el producto "
                        f"{move_line.product_id.display_name} a la ubicación "
                        f"{move_line.location_dest_id.name} por las resticciones de su "
                        "categoría. Si crees que es un error, revisa el contenido de "
                        "esta ubicación y ajusta el inventario para poder mover el "
                        "producto."
                    )
                )
        return super()._action_done()
