# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import base64
import io
import os

from odoo import _, fields, models
from odoo.exceptions import UserError

LINE_LABEL_LENGTH = 15


class SaleOrderImportEdicom(models.TransientModel):
    _name = "sale.order.import.edicom"
    _description = "Asistente de importación de pedidos EDI"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
    )
    sale_team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        required=True,
        default=lambda self: self.env["crm.team"].search([], limit=1).id,
    )
    file_ids = fields.One2many(
        comodel_name="sale.order.import.edicom.file",
        inverse_name="wizard_id",
        string="Ficheros EDI",
    )

    def action_import(self):
        self.ensure_one()
        orders = self.env["sale.order"]
        for file_line in self.file_ids:
            label = os.path.splitext(file_line.filename)[0][:LINE_LABEL_LENGTH].strip()
            orders |= self._import_orders(file_line, label)
        return {
            "name": "Presupuestos importados desde EDI",
            "context": self.env.context,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "views": [
                (self.env.ref("sale.view_order_tree").id, "tree"),
                (self.env.ref("sale.view_order_form").id, "form"),
            ],
            "domain": [("id", "in", orders.ids)],
        }

    def _get_import_config(self, conf_name="connector_edicom.sale_order_import_edicom"):
        module, ext_id = conf_name.split(".")
        try:
            record = self.env.ref(module + "." + ext_id)
            return record
        except ValueError as e:
            raise UserError(
                _(
                    "No se ha encontrado la configuración para "
                    "la importación de los ficheros EDI"
                )
            ) from e

    def _import_orders(self, file_line, label):
        self.ensure_one()
        orders = self.env["sale.order"]
        import_config = self._get_import_config()
        file_content = base64.b64decode(file_line.file)
        file_stream = io.BytesIO(file_content)
        for line in file_stream.readlines():
            line = line.decode("windows-1252").strip()
            line_configs = import_config.config_line_ids.search(
                [("file", "=", label.upper())]
            )
            vals = line_configs._compute_line_value(line)
            if label.upper() == "CABPED":
                if vals:
                    partner = self.env["res.partner"].browse(vals["partner_id"])
                    order_vals = {
                        "client_order_ref": vals.get("client_order_ref", False),
                        "partner_id": partner.commercial_partner_id.id,
                        "date_order": vals.get("date_order"),
                        "edicom_order_id": vals.get("edicom_order_id", False),
                        "team_id": self.sale_team_id.id,
                        "commitment_date": vals.get("commitment_date", False),
                    }
                    for key in ["partner_shipping_id", "partner_invoice_id"]:
                        if vals.get(key):
                            order_vals[key] = vals[key]
                    sale_order = self.env["sale.order"].create(order_vals)
                    orders |= sale_order
            elif label.upper() == "OBSPED":
                continue  # TODO: Implementar la importación de las observaciones
            elif label.upper() == "LINPED":
                if not vals.get("edicom_order_id_line"):
                    continue
                edicom_order_id_line = vals["edicom_order_id_line"]
                sale_order = self.env["sale.order"].search(
                    [("edicom_order_id", "=", edicom_order_id_line)]
                )
                if not sale_order:
                    raise UserError(
                        _(
                            "No se ha encontrado ningún "
                            "pedido con ID EDI: {edicom_order_id_line}"
                        )
                    )
                elif len(sale_order) > 1:
                    raise UserError(
                        _(
                            "Se han encontrado varios pedidos "
                            "con el mismo ID EDI: {edicom_order_id_line}"
                        )
                    )
                product = self.env["product.product"].browse(vals["product_id"])
                product_uom_qty = vals.get("product_uom_qty", 0)
                name = vals.get("name", False)
                new_line = self.env["sale.order.line"].new(
                    {
                        "order_id": sale_order.id,
                        "product_id": product.id,
                        "product_uom_qty": product_uom_qty,
                        "name": name,
                        "price_unit": vals.get("price_unit", 0.0),
                    }
                )
                new_line._compute_name()
                new_line._compute_price_unit()
                new_line._compute_product_packaging_qty()
                new_line._compute_tax_id()
                values = new_line._convert_to_write(new_line._cache)
                if not values.get("product_id"):
                    raise UserError(
                        _(f"El producto {name} no se ha podido encontrar en el sistema")
                    )
                self.env["sale.order.line"].create(values)
                if sale_order not in orders:
                    orders |= sale_order
        return orders


class SaleOrderImportEdicomFile(models.TransientModel):
    _name = "sale.order.import.edicom.file"
    _description = "Ficheros EDI para asistente de importación de pedidos"

    wizard_id = fields.Many2one(
        comodel_name="sale.order.import.edicom",
        string="Asistente de importación EDI",
    )
    file = fields.Binary(string="Fichero EDI", required=True)
    filename = fields.Char(string="Nombre fichero")
