# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    use_date = fields.Datetime(
        string="Fecha de consumo preferente",
        help="Fecha en la que el lote debe ser consumido",
        copy=False,
    )

    def _get_stock_barcode_data(self):
        """Cargar empaquetados y sus productos, ya que la
        primera vez no se cargan y no se reconocen  en el inventario
        al escanear un código GS1"""
        data = super()._get_stock_barcode_data()
        data["records"].setdefault("product.packaging", [])
        data["records"]["product.packaging"] = (
            self.env["product.packaging"]
            .search([("barcode", "!=", False)])
            .read(self.env["product.packaging"]._get_fields_stock_barcode(), load=False)
        )
        data["records"].setdefault("product.product", [])
        data["records"]["product.product"] += (
            self.env["product.product"]
            .search([("barcode", "!=", False)])
            .read(self.env["product.product"]._get_fields_stock_barcode(), load=False)
        )
        return data

    @api.model
    def barcode_write(self, vals):
        """Actualizar fecha de caducidad y/o fecha de consumo preferente,
        cuando el sistema genera un lote nuevo al escanear un código GS1"""
        lots = {}
        for val in vals:
            if val[0] in (0, 1) and not val[2].get("lot_id") and val[2].get("lot_name"):
                lot_dates = {}
                use_date = val[2].pop("use_date", None)
                if use_date:
                    lot_dates["use_date"] = use_date
                expiration_date = val[2].pop("expiration_date", None)
                if expiration_date:
                    lot_dates["expiration_date"] = expiration_date
                lots.setdefault(val[2]["lot_name"], lot_dates)
        res = super().barcode_write(vals)
        for lot_name, lot_vals in lots.items():
            lot = self.env["stock.lot"].search([("name", "=", lot_name)], limit=1)
            if lot:
                lot.write(lot_vals)
        return res

    @api.model
    def _get_inventory_fields_write(self):
        return ["use_date", "expiration_date"] + super()._get_inventory_fields_write()
