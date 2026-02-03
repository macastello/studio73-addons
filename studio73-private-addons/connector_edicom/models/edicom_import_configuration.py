# copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)


import logging
from datetime import datetime

from odoo import _, exceptions, fields, models

_LOGGER = logging.getLogger(__name__)

VALORES_PERMITIDOS = {
    "CABPED": {
        "NODO": {
            "220": "Pedido",
            "221": "Pedido abierto",
            "224": "Pedido urgente",
            "226": "Pedido parcial (cancelación de pedido abierto)",
            "227": "Pedido en consignación",
            "22E": "Propuesta de pedido del proveedor (CRP)",
            "YB1": "Pedido de Cross Docking",
        },
        "FUNCION": {
            "3": "Cancelación",
            "5": "Reemplazar",
            "6": "Confirmación",
            "7": "Duplicado",
            "9": "Original",
            "31": "Copia",
            "16": "Propuesta (CRP)",
            "46": "Provisional",
        },
        "FORMAPAG": {
            "42": "Pago a una cuenta bancaria",
            "14E": "Pago mediante giro bancario",
            "10": "En efectivo",
            "20": "Cheque",
            "60": "Pagaré",
        },
        "CONDESP": {
            "X2": "Si envío parcial entregar resto pedido",
            "X41": "Pedido reserva cliente",
            "X42": "Pedido online",
            "X43": "Pedido stock de seguridad",
        },
    },
    "OBSPED": {},
    "LINPED": {},
    "OBSLPED": {},
    "LOCLPED": {},
}


class EdicomImportConfig(models.Model):
    _name = "edicom.import.config"
    _description = "EDI Import Config"

    name = fields.Char(string="Name", required=True)
    dir = fields.Char(string="Files dir", required=True)
    version = fields.Char(string="Version", required=True)
    config_line_ids = fields.One2many(
        comodel_name="edicom.import.config.line",
        inverse_name="import_config_id",
        string="Lines",
    )


class EdicomImportConfigLine(models.Model):
    _name = "edicom.import.config.line"
    _description = "EDI Import Config Line"
    _order = "sequence ASC"

    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string="Field")
    field_name = fields.Char(string="Odoo field")
    type = fields.Selection(
        string="Odoo field type",
        selection=[
            ("integer", "Integer"),
            ("float", "Float"),
            ("text", "Text"),
            ("date", "Date"),
            ("datetime", "Datetime"),
            ("m2o", "Many2one"),
            ("m2m", "Many2many"),
            ("valp", "Valores permitidos"),
        ],
        default="text",
    )
    model = fields.Char(string="Odoo model")
    search_field = fields.Char(string="Search field")
    file = fields.Selection(
        string="File name",
        selection=[
            ("CABPED", "CABPED"),
            ("OBSPED", "OBSPED"),
            ("LINPED", "LINPED"),
            ("OBSLPED", "OBSLPED"),
            ("LOCLPED", "LOCLPED"),
        ],
        required=True,
    )
    decimal_length = fields.Integer(string="Decimal length")
    dimension = fields.Integer(string="Length", required=True)
    description = fields.Char(string="Description")
    import_config_id = fields.Many2one(
        comodel_name="edicom.import.config", string="Import configuration"
    )
    line_id = fields.Many2one(
        comodel_name="edicom.import.config.line", string="Parent line"
    )
    line_ids = fields.One2many(
        comodel_name="edicom.import.config.line",
        inverse_name="import_config_id",
        string="Lines",
    )

    def _get_value(self, pos, line):
        self.ensure_one()
        val = line[pos : pos + self.dimension].strip()
        return val

    def _parse_integer(self, value):
        self.ensure_one()
        try:
            return int(value)
        except ValueError:
            _LOGGER.info("Error parsing to integer %s", self.name)
            return False

    def _parse_float(self, value):
        self.ensure_one()
        if not value:
            return False
        try:
            float_str = (
                value[: -self.decimal_length] + "." + value[-self.decimal_length :]
            )
            return float(float_str)
        except ValueError:
            _LOGGER.info("Error parsing to float %s", self.name)
            return False

    def _parse_text(self, value):
        self.ensure_one()
        return value

    def _parse_date(self, value):
        self.ensure_one()
        try:
            date = datetime.strptime(value, "%Y%m%d")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            _LOGGER.info("Error parsing to date %s", self.name)
            return False

    def _parse_datetime(self, value):
        self.ensure_one()
        try:
            value = value.decode() if isinstance(value, bytes) else value
            date = datetime.strptime(value, "%Y%m%d%H%M")
            return date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            _LOGGER.info("Error parsing to datetime %s", self.name)
            return False

    def _parse_m2o(self, value):
        self.ensure_one()
        value = value.decode() if isinstance(value, bytes) else value
        res = []
        if self.model and self.name and self.search_field:
            res = self.env[self.model].search(
                [(self.search_field, "=", value)], limit=1
            )
            if not res and self.search_field == "barcode":
                eans_to_ignore = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("connector_edicom.ignored_ean", [])
                )
                if value not in eans_to_ignore:
                    raise exceptions.UserError(
                        _(
                            "Error al importar pedido: No se ha encontrado "
                            "ningún producto "
                            "en el sistema con Barcode (EAN13) %s",
                            value,
                        )
                    )
        if self.model == "res.partner" and not res:
            raise exceptions.UserError(
                _(
                    "No se ha encontrado ningún cliente/dirección para el "
                    "campo %s, el EAN13 recibido es %s",
                    self.name,
                    value,
                )
            )
        return res and res.id or res

    def _parse_m2m(self, value):
        self.ensure_one()
        res = []
        if self.model and self.name and self.search_field:
            element = self.env[self.model].search(
                [(self.search_field, "=", value)], limit=1
            )
            if element:
                res.append((4, element.id, None))
        return res

    def _parse_valp(self, value):
        self.ensure_one()
        value = value.decode().strip() if isinstance(value, bytes) else value.strip()
        return VALORES_PERMITIDOS[self.file][self.name].get(value, value)

    def _compute_line_value(self, file_line):
        pos = 0
        vals = {}
        for line in self:
            value = line._get_value(pos, file_line)
            value = value.strip() if isinstance(value, bytes) else value.strip()
            try:
                if line.type == "integer":
                    value = line._parse_integer(value)
                elif line.type == "float":
                    value = line._parse_float(value)
                elif line.type == "text":
                    value = line._parse_text(value)
                elif line.type == "date":
                    value = line._parse_date(value)
                elif line.type == "datetime":
                    value = line._parse_datetime(value)
                elif line.type == "m2o":
                    value = line._parse_m2o(value)
                elif line.type == "m2m":
                    value = line._parse_m2m(value)
                elif line.type == "valp":
                    value = line._parse_valp(value)
            except Exception as e:
                _LOGGER.info(
                    "Error parsing %s with value %s: %s", line.field_name, value, e
                )
                value = False
            vals.update({line.field_name: value})
            pos += line.dimension
        return vals
