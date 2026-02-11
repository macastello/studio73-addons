# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    stock_barcode_add_new_product = fields.Boolean(
        string="¿Permitir añadir producto PDA?",
        help="Permitir añadir nuevos productos, de forma manual, en la interfaz de "
        "códigos de barra, mostrando el botón correspondiente",
        default=True,
        copy=False,
    )
    stock_barcode_allow_scan_extra_qty = fields.Boolean(
        string="¿Permitir más cantidad de la reservada en PDA?",
        help="Si se marca la casilla, en la interfaz de código de barras se permitirá "
        "escanear más cantidad de la reservada",
        copy=False,
    )
    stock_barcode_force_increment = fields.Boolean(
        string="Forzar sumar cantidad al escanear producto",
        help="Si se marca la casilla, en la interfaz de código de barras se "
        "sumará cantidad a la línea al escanear producto incluso si el producto de "
        "esta tiene seguimiento por lotes",
        copy=False,
    )
    stock_barcode_groupby_loc_and_prod = fields.Boolean(
        string="Agrupar líneas por ubicación y producto",
        help="permite agrupar las líneas de albarán por ubicación y referencia "
        "independientemente del albaran donde provenga",
        copy=False,
    )
    stock_barcode_close_partial_batch = fields.Boolean(
        string="PDA Agrupaciones: Cerrar agrupación parcial",
        help="Si se marca la casilla, en la interfaz de código de barras se "
        "cerrará pantalla de la agrupación al validarse incluso si aún quedan líneas "
        "por validar",
        copy=False,
    )
    show_counter_lines = fields.Boolean(
        string="Mostrar contador de líneas",
        help="En la vista tablet de código de barras si se activa este check, "
        "se muestra un contado de líneas con la cantidad actualizada",
        copy=False,
    )
    stock_barcode_avoid_grouped_lines = fields.Boolean(
        string="PDA: Evitar agrupar líneas",
        help=(
            "Si este campo está marcado, en la vista tablet de código de barras de "
            "albaranes y agrupaciones no se agruparán las líneas en sublíneas para "
            "facilitar su preparación"
        ),
        copy=False,
    )
    stock_barcode_restrict_products = fields.Boolean(
        string="Restringir escaneo a productos del albarán",
        help="Si se marca la casilla, solo se permitirá escanear productos del "
        "albarán y lotes y paquetes que los contienen.",
        copy=False,
    )
    stock_barcode_allow_any_dest_location = fields.Boolean(
        string="Permitir cualquier ubicación destino",
        help=(
            "Si este campo está marcado, en la vista tablet de código de barras de "
            "albaranes y agrupaciones se permitirá escanear cualquier ubicación "
            "destino, independientemente de si cuelga o no de la ubicación destino "
            "del albarán/tipo de operación"
        ),
        copy=False,
    )
    apply_dest_location_all_lines = fields.Boolean(
        string="PDA: Aplicar ubicación destino a todas las líneas",
        help="En la vista tablet de código de barras de agrupaciones si se activa este "
        "check, cuando se escanee la ubicación destino se aplicará a todas las líneas"
        " con cantidad en hecho incluso si esta no cuelga de la ubicación destino del "
        "albarán",
        copy=False,
    )
    stock_barcode_restrict_location = fields.Boolean(
        string="Restricción de ubicación",
        help="Si se marca la casilla, solo se permitirá escanear ubicaciones que "
        "estén presentes en las líneas del albarán/lote.",
        copy=False,
    )

    def _get_barcode_config(self):
        self.ensure_one()
        config = super()._get_barcode_config()
        config.update(
            {
                "add_new_product": self.stock_barcode_add_new_product,
                "allow_scan_extra_qty": self.stock_barcode_allow_scan_extra_qty,
                "force_qty_increment_at_scan": self.stock_barcode_force_increment,
                "close_partial_batch": self.stock_barcode_close_partial_batch,
                "show_counter_lines": self.show_counter_lines,
                "groupby_loc_and_prod": self.stock_barcode_groupby_loc_and_prod,
                "avoid_grouped_lines": self.stock_barcode_avoid_grouped_lines,
                "stock_barcode_restrict_products": self.stock_barcode_restrict_products,
                "allow_any_dest_location": self.stock_barcode_allow_any_dest_location,
                "apply_dest_location_all_lines": self.apply_dest_location_all_lines,
                "stock_barcode_restrict_location": self.stock_barcode_restrict_location,
            }
        )
        return config
