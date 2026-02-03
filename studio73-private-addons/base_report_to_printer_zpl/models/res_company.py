# Copyright 2023 Studio73 - Guillermo Llinares <guillermo@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
try:
    from PIL import Image
    from zplgrf import GRF
except ImportError:
    GRF = object
    Image = object
import base64
from io import BytesIO

from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def get_zpl_logo(self, name, image=None, size=200, rotate=0):
        self.ensure_one()
        if not image:
            image = self.logo
            if not image:
                return ""
        # Resize image
        img = Image.open(BytesIO(base64.b64decode(self.logo)))
        img_sized = img.resize((size, int(img.size[1] * size / img.size[0])))
        if rotate:
            img_sized = img_sized.rotate(rotate, expand=True)
        bytes_img = BytesIO()
        img_sized.save(bytes_img, format=img.format)
        # Convert to ZPL
        grf = GRF.from_image(bytes_img.getvalue(), name)
        zpl_code = grf.to_zpl(compression=3, quantity=1)
        return zpl_code[: zpl_code.find("^XA")]
