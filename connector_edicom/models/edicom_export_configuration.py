# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class EdicomExportConfiguration(models.Model):
    _name = "edicom.export.configuration"
    _description = "Edicom Export Configuration"

    name = fields.Char(string="Name")
    model_number = fields.Char(string="Model Number", size=3)
    model = fields.Many2one(
        comodel_name="ir.model", string="Odoo Model", ondelete="cascade"
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    config_lines = fields.One2many(
        "edicom.export.configuration.line",
        inverse_name="export_config_id",
        string="Configuration Lines",
    )
    dir = fields.Char(string="Directory")
    version = fields.Char(string="Version")


class EdicomExportConfigurationLine(models.Model):
    _name = "edicom.export.configuration.line"
    _description = "Edicom Export Configuration Line"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence")
    export_config_id = fields.Many2one(
        comodel_name="edicom.export.configuration",
        string="Export Configuration",
        ondelete="cascade",
        required=True,
    )
    name = fields.Char(string="Field Name", required=True)
    repeat_expression = fields.Char(
        string="Repeat Expression",
        help="If set, this expression will be used to getting "
        "the list of elements to iterate on",
    )
    repeat = fields.Boolean(compute="_compute_repeat", store=True)
    conditional_expression = fields.Char(
        string="Conditional Expression",
        help="If set, this expression will be used to evaluate "
        "if this line should be included in the export",
    )
    conditional = fields.Boolean(compute="_compute_conditional", store=True)
    sub_config = fields.Many2one(
        comodel_name="edicom.export.configuration", string="Sub Configuration"
    )
    export_type = fields.Selection(
        selection=[
            ("string", "Alphanumeric"),
            ("integer", "Number without decimals"),
            ("float", "Number with decimals"),
            ("boolean", "Boolean"),
            ("date", "Date"),
            ("datetime", "Datetime"),
            ("subconfig", "Sub Configuration"),
        ],
        string="Export Field Type",
        default="string",
        required=True,
    )
    apply_sign = fields.Boolean(string="Apply Sign", default=True)
    positive_sign = fields.Char(string="Positive Sign Character", default="+", size=1)
    negative_sign = fields.Char(string="Negative Sign Character", default="-", size=1)
    size = fields.Integer(string="Field Size")
    alignment = fields.Selection(
        selection=[("left", "Left"), ("right", "Right")],
        string="Alignment",
        default="left",
    )
    bool_no = fields.Char(string="Value for no", default=" ", size=1)
    bool_yes = fields.Char(string="Value for yes", default="X", size=1)
    decimal_size = fields.Integer(string="Number of Char for decimals", default=0)
    expression = fields.Char(string="Expression")
    fixed_value = fields.Char(string="Fixed Value")
    position = fields.Integer(compute="_compute_position")
    required = fields.Boolean(string="Required", default=False)
    value = fields.Char(compute="_compute_value", store=True)

    @api.depends("repeat_expression")
    def _compute_repeat(self):
        for line in self:
            line.repeat = bool(line.repeat_expression)

    @api.depends("conditional_expression")
    def _compute_conditional(self):
        for line in self:
            line.conditional = bool(line.conditional_expression)

    @api.depends("sequence")
    def _compute_position(self):
        for line in self:
            line.position = 1
            for line2 in line.export_config_id.config_lines:
                if line2 == line:
                    break
                line.position += line2.size

    @api.depends("fixed_value", "expression")
    def _compute_value(self):
        for line in self:
            if line.export_type == "subconfig":
                line.value = "-"
            elif line.expression:
                line.value = _("Expression: ")
                if len(line.expression) > 35:
                    line.value += f"{line.expression[34]}"
                else:
                    line.value += f"{line.expression}"
            else:
                line.value = _(f'Fixed {line.fixed_value or _("<blank>")}')

    @api.onchange("export_type")
    def onchange_type(self):
        if self.export_type in ("float", "integer"):
            self.alignment = "right"
        elif self.export_type in ("string", "boolean"):
            self.alignment = "left"

    @api.onchange("sub_config")
    def onchange_sub_config(self):
        if self.sub_config:
            self.update(
                {
                    "export_type": False,
                    "decimal_size": 0,
                    "alignment": False,
                    "apply_sign": False,
                }
            )
