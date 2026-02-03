# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


def pre_init_hook(env):
    if openupgrade.is_module_installed(env.cr, "stock_barcode_inventory_gs1"):
        openupgrade.update_module_names(
            env.cr,
            [("stock_barcode_inventory_gs1", "stock_barcode_gs1")],
            merge_modules=True,
        )
