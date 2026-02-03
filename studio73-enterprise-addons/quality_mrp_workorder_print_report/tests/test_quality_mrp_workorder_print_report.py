# Copyright 2024 Studio73 - Alex Garcia <alex@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestQualityCheck(TransactionCase):
    def setUp(self):
        super().setUp()
        default_team_id = self.env["quality.alert.team"].search([], limit=1).id
        # Crear el centro de trabajo
        self.workcenter = self.env["mrp.workcenter"].create(
            {
                "name": "Work Center 1",
                "code": "WC1",
            }
        )

        self.report = self.env["ir.actions.report"].create(
            {
                "name": "Informe de Prueba",
                "report_name": "quality_check_report",  # Campo agregado
                "model": "quality.check",
                "report_type": "qweb-pdf",
            }
        )

        self.producto_sin_seguimiento = self.env["product.product"].create(
            {
                "name": "Producto Sin Seguimiento",
                "tracking": "none",
            }
        )

        self.producto_con_seguimiento = self.env["product.product"].create(
            {
                "name": "Producto Con Seguimiento",
                "tracking": "lot",
            }
        )

        self.lote = self.env["stock.lot"].create(
            {
                "name": "Lote 001",
                "product_id": self.producto_con_seguimiento.id,
            }
        )

        bom_data = {
            "product_tmpl_id": self.producto_con_seguimiento.product_tmpl_id.id,
            "product_uom_id": self.producto_con_seguimiento.uom_id.id,
        }

        bom_id = self.env["mrp.bom"].create(bom_data).id

        self.orden_produccion = self.env["mrp.production"].create(
            {
                "product_id": self.producto_con_seguimiento.id,
                "product_qty": 10.0,
                "product_uom_id": self.producto_con_seguimiento.uom_id.id,
                "bom_id": bom_id,
            }
        )

        self.orden_produccion = self.env["mrp.production"].create(
            {
                "product_id": self.producto_con_seguimiento.id,
                "product_qty": 10.0,
                "product_uom_id": self.producto_con_seguimiento.uom_id.id,
                "bom_id": bom_id,
            }
        )

        self.orden_trabajo = self.env["mrp.workorder"].create(
            {
                "name": "Orden de Trabajo Prueba",  # Asignar un nombre descriptivo
                "product_id": self.producto_con_seguimiento.id,
                "finished_lot_id": self.lote.id,
                "workcenter_id": self.workcenter.id,
                "product_uom_id": self.producto_con_seguimiento.uom_id.id,
                "production_id": self.orden_produccion.id,
            }
        )

        self.control_calidad = self.env["quality.check"].create(
            {
                "point_id": self.env["quality.point"]
                .create({"report_id": self.report.id})
                .id,
                "workorder_id": self.orden_trabajo.id,
                "product_id": self.producto_sin_seguimiento.id,
                "team_id": default_team_id,
            }
        )

    def test_action_print_sin_report_id(self):
        """Caso de prueba donde no se establece report_id."""
        self.control_calidad.point_id.report_id = False
        result = self.control_calidad.action_print()
        self.assertEqual(
            result,
            super(type(self.control_calidad), self.control_calidad).action_print(),
        )

    def test_action_print_sin_finished_lot_id(self):
        self.control_calidad.product_id = self.producto_con_seguimiento
        self.control_calidad.workorder_id.finished_lot_id = False
        self.control_calidad.point_id.copies_number = 2
        with self.assertRaises(UserError) as cm:
            self.control_calidad.action_print()
        self.assertEqual(
            str(cm.exception),
            _("You did not set a lot/serial number for the final product"),
        )

    def test_action_print_con_report_id(self):
        self.control_calidad.product_id = self.producto_con_seguimiento
        self.control_calidad.point_id.copies_number = 2
        self.control_calidad.point_id.report_model = "stock.lot"
        self.control_calidad.workorder_id.finished_lot_id = (
            self.lote.id
        )  # Asignar un lote válido
        result = self.control_calidad.action_print()
        expected_action = self.control_calidad.point_id.report_id.report_action(
            [self.control_calidad.workorder_id.finished_lot_id.id]
            * self.control_calidad.point_id.copies_number
        )
        self.assertEqual(result.get("id"), expected_action.get("id"))
        self.assertEqual(result.get("type"), expected_action.get("type"))
        self.assertEqual(result.get("active_ids"), expected_action.get("active_ids"))
