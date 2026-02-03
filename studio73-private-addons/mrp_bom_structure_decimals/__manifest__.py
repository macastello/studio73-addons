# Copyright 2020 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "MRP BoM Structure Decimals",
    "license": "LGPL-3",
    "author": "Studio73",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "category": "Manufacturing",
    "version": "17.0.1.0.0",
    "depends": ["mrp"],
    "data": ["data/product_data.xml", "report/mrp_report_bom_structure.xml"],
    "assets": {
        "web.assets_backend": [
            "mrp_bom_structure_decimals/static/src/**/*",
        ],
    },
}
