# Copyright 2021 Studio73 - Guillermo Llinares - <guillermo@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Report to printer ZPL",
    "version": "17.0.1.0.0",
    "summary": """Poder enviar informes tipo text directamente a la impresora.""",
    "license": "LGPL-3",
    "category": "Generic Modules/Base",
    "author": "Studio73",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["base_report_to_printer"],
    "data": [
        "report/report_templates.xml",
        "views/ir_actions_report_views.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["zplgrf", "Pillow"]},
}
