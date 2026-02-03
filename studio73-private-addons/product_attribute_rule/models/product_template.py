# Copyright 2020 Studio73 - Pablo Fuentes <pablo@studio73.es>
# Copyright 2023 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, tools


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _is_combination_possible_by_config(self, combination, ignore_no_variant=False):
        self.ensure_one()
        rule = self.env["product.attribute.rule.line"].search(
            self._get_affecting_rules_domain(combination.product_attribute_value_id),
            limit=1,
        )
        if rule:
            return False
        return super()._is_combination_possible_by_config(
            combination, ignore_no_variant=ignore_no_variant
        )

    def _get_own_attribute_exclusions(self, combination_ids=None):
        self.ensure_one()
        exclusions = super()._get_own_attribute_exclusions(
            combination_ids=combination_ids
        )
        return self._get_own_attribute_exclusions_ext(exclusions=exclusions)

    @tools.ormcache("self")
    def _get_own_attribute_exclusions_ext(self, exclusions=None):
        if exclusions is None:
            exclusions = {}
        rule_obj = self.env["product.attribute.rule.line"]
        ptva_obj = self.env["product.template.attribute.value"]
        attribute_values = (
            self.valid_product_template_attribute_line_ids.product_template_value_ids
        )
        for ptav in attribute_values:
            domain = self._get_affecting_rules_domain(no_values=True)
            domain.append(("value_x", "=", ptav.product_attribute_value_id.id))
            rule_ids = rule_obj.search(domain).value_y.ids
            value_ids = ptva_obj.search(
                [
                    ("product_attribute_value_id", "in", rule_ids),
                    ("product_tmpl_id", "=", self.id),
                ]
            ).ids
            exclusions.setdefault(ptav.id, []).extend(value_ids)
            exclusions[ptav.id] = list(set(exclusions[ptav.id]))
        return exclusions

    def _get_affecting_rules_domain(self, values=False, no_values=False):
        domain = [
            ("rule_id", "!=", False),
            ("rule_id.exclude_product_tmpl_ids", "not in", self.ids),
            "|",
            ("rule_id.product_tmpl_ids", "=", False),
            ("rule_id.product_tmpl_ids", "in", self.ids),
            "|",
            "&",
            ("action", "=", "restrict"),
            ("available", "=", True),
            "&",
            ("action", "=", "combine"),
            ("available", "=", False),
        ]
        if not no_values:
            values = values or self.valid_product_template_attribute_line_ids.value_ids
            domain.extend(
                [("value_x", "in", values.ids), ("value_y", "in", values.ids)]
            )
        return domain

    def action_open_attribute_rules(self):
        self.ensure_one()
        return {
            "name": "Restricciones",
            "type": "ir.actions.act_window",
            "res_model": "product.attribute.rule.line",
            "views": [[False, "tree"], [False, "form"]],
            "domain": self._get_affecting_rules_domain(),
            "search_view_id": self.env.ref(
                "product_attribute_rule.product_attribute_rule_line_search"
            ).id,
        }
