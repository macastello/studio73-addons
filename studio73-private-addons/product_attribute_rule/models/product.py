# Copyright 2020 Studio73 - Pablo Fuentes <pablo@studio73.es>
# Copyright 2023 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command, _, api, exceptions, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        """Si un producto se tiene que volver a activar según los atributos asignados
        en la plantilla, se tiene que comprobar también que no haya ninguna regla que
        impida esa combinación, para evitar que se activen"""
        if not vals.get("active"):
            return super().write(vals)
        for product in self:
            product_vals = vals.copy()
            value_ids = product.product_template_attribute_value_ids
            value_ids = value_ids.product_attribute_value_id.ids
            product_tmpl_id = product.product_tmpl_id.id
            rule = self._find_attribute_rule(product_tmpl_id, value_ids=value_ids)
            if rule:
                product_vals.pop("active", None)
            super(ProductProduct, product).write(product_vals)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        vals_list_filtered = []
        for vals in vals_list:
            att_tmpl_val_ids = vals.get("product_template_attribute_value_ids")
            product_tmpl_id = vals.get("product_tmpl_id", False)
            if att_tmpl_val_ids:
                att_val_ids = (
                    self.env["product.template.attribute.value"]
                    .search([("id", "in", att_tmpl_val_ids[0][2])])
                    .product_attribute_value_id.ids
                )
                if att_val_ids:
                    rule = self._find_attribute_rule(
                        product_tmpl_id, value_ids=att_val_ids
                    )
                    if rule:
                        continue
                vals_list_filtered.append(vals)
            else:
                vals_list_filtered.append(vals)
        return super().create(vals_list_filtered)

    def _unlink_or_archive(self, check_access=True):
        do_archive = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("product_attribute_rule.archive_variants")
        )
        if do_archive:
            self.write({"active": False})
        else:
            super()._unlink_or_archive()

    def _find_attribute_rule(self, product_tmpl_id, value_ids=None):
        if value_ids is None:
            value_ids = []
        domain = [
            ("value_x", "in", value_ids),
            ("value_y", "in", value_ids),
            ("rule_id", "!=", False),
            ("rule_id.exclude_product_tmpl_ids", "not in", [product_tmpl_id]),
            "|",
            ("rule_id.product_tmpl_ids", "=", False),
            ("rule_id.product_tmpl_ids", "in", [product_tmpl_id]),
            "|",
            "&",
            ("action", "=", "restrict"),
            ("available", "=", True),
            "&",
            ("action", "=", "combine"),
            ("available", "=", False),
        ]
        return self.env["product.attribute.rule.line"].search(domain, limit=1)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    rule_ids = fields.One2many(
        comodel_name="product.attribute.rule", string="Reglas", compute="_compute_rules"
    )

    def _compute_rules(self):
        for record in self:
            rules = self.env["product.attribute.rule"].search(
                [
                    "|",
                    ("attribute_x_id", "=", record.id),
                    ("attribute_y_id", "=", record.id),
                ]
            )
            record.rule_ids = rules


class ProductAttributeRule(models.Model):
    _name = "product.attribute.rule"
    _description = "Product attribute rule"
    _order = "sequence"

    sequence = fields.Integer(string="Secuencia")
    name = fields.Char(string="Nombre")
    action = fields.Selection(
        string="Acción",
        selection=[("combine", "Combinar"), ("restrict", "Restringir")],
        default="restrict",
        required=True,
    )
    attribute_x_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Atributo X",
        required=True,
        ondelete="restrict",
    )
    attribute_y_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Atributo Y",
        required=True,
        ondelete="restrict",
    )
    rule_line_ids = fields.One2many(
        comodel_name="product.attribute.rule.line",
        inverse_name="rule_id",
        string="Rule Lines",
        copy=True,
    )
    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Productos que aplican",
        domain=[("type", "!=", "service")],
        help="Si la regla es aplicable solo a algunos productos en concreto, debemos "
        "establecer aquí esos productos. Si este campo se deja vacío, significa que "
        "la regla se aplica de forma genérica, a todos los productos",
    )
    exclude_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_attribute_rule_exclude_template_rel",
        column1="rule_id",
        column2="product_tmpl_id",
        string="Productos excluidos",
        domain=[("type", "!=", "service")],
        help="Productos para los cuales no deben aplicarse estas reglas. Este campo se "
        "habilita especialmente para facilitar la gestión de las reglas que no deben "
        "aplicarse a ciertos productos, pero como las reglas están creadas de forma "
        "genérica, es difícil averiguar cuales son los productos que si aplican, para "
        "aplicarlas únicamente a esos productos",
    )

    def _get_products(self):
        self.ensure_one()
        products = self.product_tmpl_ids
        if not products and self.exclude_product_tmpl_ids:
            products = (
                self.env["product.template"].search([]) - self.exclude_product_tmpl_ids
            )
        return products

    def _get_default_rule_lines(self):
        lines = []
        attribute_x = self.attribute_x_id
        attribute_y = self.attribute_y_id
        products = self._get_products()
        values = products.attribute_line_ids.value_ids.ids
        for value_x in attribute_x.value_ids:
            for value_y in attribute_y.value_ids:
                if not values or (value_x.id in values and value_y.id in values):
                    vals = {
                        "value_x": value_x.id,
                        "value_y": value_y.id,
                        "available": False,
                        "rule_id": self.id,
                    }
                    lines.append(Command.create(vals))
        return lines

    def _init_lines(self):
        if self.rule_line_ids:
            return
        self.rule_line_ids = self._get_default_rule_lines()

    def action_update_lines(self):
        lines = []
        x_values = self.attribute_x_id.value_ids
        y_values = self.attribute_y_id.value_ids
        products = self._get_products()
        product_values = products.attribute_line_ids.value_ids
        # Si tenemos productos especificados, solo queremos crear lineas de atributos
        # suyos. (& = set.intersection)
        if product_values:
            x_values &= product_values
            y_values &= product_values
        created_combinations = []
        # Itera por todos los atributos X y solo crea reglas para los nuevos
        # Empezamos con estas reglas antes de darle al botón:
        #     1  2
        #   |-----
        # A | X  X
        # B | X  X
        # C | X  X
        # Se crean el valor de atributo X nuevo 3 y atributo Y nuevo D
        # En el primer bucle crea las reglas para los atributos X nuevos
        # O = Creando nuevo, X = Ya existente
        #     1  2  3
        #   |---------
        # A | X  X  O
        # B | X  X  O
        # C | X  X  O
        # D |       O
        for value_x in x_values:
            if value_x in self.rule_line_ids.value_x:
                continue
            for value_y in y_values:
                created_combinations.append((value_x.id, value_y.id))
                lines.append(
                    Command.create(
                        {
                            "value_x": value_x.id,
                            "value_y": value_y.id,
                            "available": False,
                            "rule_id": self.id,
                        }
                    )
                )
        # Aquí solo mira el atributo D, porque los otros ya existen. El D3 se lo salta
        # porque ya se ha creado antes (created_combinations)
        #     1  2  3
        #   |---------
        # A | X  X  X
        # B | X  X  X
        # C | X  X  X
        # D | O  O  X
        for value_x in x_values:
            for value_y in y_values:
                if (
                    value_y in self.rule_line_ids.value_y
                    or (value_x.id, value_y.id) in created_combinations
                ):
                    continue
                lines.append(
                    Command.create(
                        {
                            "value_x": value_x.id,
                            "value_y": value_y.id,
                            "available": False,
                            "rule_id": self.id,
                        }
                    )
                )
        if lines:
            self.rule_line_ids = lines

    @api.constrains("attribute_x_id", "attribute_y_id")
    def _check_attribute_id(self):
        for record in self:
            if record.attribute_x_id == record.attribute_y_id:
                raise exceptions.ValidationError(
                    _("No puedes combinar/restringir el mismo atributo")
                )

    @api.onchange("action")
    def _onchange_action(self):
        if self.attribute_x_id and self.attribute_y_id and self.action:
            action_str = dict(self._fields["action"].selection).get(self.action)
            self.name = "{} {} / {}".format(
                action_str, self.attribute_x_id.name, self.attribute_y_id.name
            )
            self._init_lines()

    @api.onchange("attribute_x_id", "attribute_y_id")
    def _onchange_attribute_ids(self):
        if self.attribute_x_id and self.attribute_y_id and self.action:
            self.rule_line_ids.unlink()
            self._onchange_action()


class ProductAttributeRuleLine(models.Model):
    _name = "product.attribute.rule.line"
    _description = "Product attribute rule lines"

    rule_id = fields.Many2one(
        comodel_name="product.attribute.rule", string="Regla", ondelete="cascade"
    )
    sequence = fields.Integer(string="Secuencia", related="rule_id.sequence")
    action = fields.Selection(string="Acción", related="rule_id.action")
    value_x = fields.Many2one(comodel_name="product.attribute.value")
    value_y = fields.Many2one(comodel_name="product.attribute.value")
    available = fields.Boolean(string="Disponible")
