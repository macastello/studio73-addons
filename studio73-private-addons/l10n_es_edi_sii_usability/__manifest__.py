# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "España - SII EDI Usability",
    "version": "17.0.1.8.6",
    "summary": "Configurar modo de envío de las facturas al SII",
    "license": "LGPL-3",
    "author": "Studio73",
    "category": "Invoicing Management",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["l10n_es_edi_sii"],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
