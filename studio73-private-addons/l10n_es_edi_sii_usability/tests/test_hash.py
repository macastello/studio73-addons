# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import hashlib
import inspect

from odoo.tests.common import TransactionCase

from odoo.addons.account_edi.models.account_move import AccountMove as move_upstream
from odoo.addons.l10n_es_edi_sii.models.account_edi_format import (
    AccountEdiFormat as move_sii,
)

VALID_HASHES = {
    "_post": "8028651cd990b9a357bdb41f76047546",
    "_l10n_es_edi_call_web_service_sign_common": "4a8b927adbde9b0b74288ed1d3e40659",
    "_l10n_es_edi_get_invoices_info": "e26477124cbabf224da844f04d790f3f",
}


class TestSaleOrder(TransactionCase):
    def test_hash_compute_advance_payment(self):
        func = inspect.getsource(move_upstream._post).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertEqual(func_hash, VALID_HASHES["_post"])

    def test_hash_web_service_sign(self):
        func = inspect.getsource(
            move_sii._l10n_es_edi_call_web_service_sign_common
        ).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertEqual(
            func_hash, VALID_HASHES["_l10n_es_edi_call_web_service_sign_common"]
        )

    def test_hash_get_invoices_info(self):
        func = inspect.getsource(move_sii._l10n_es_edi_get_invoices_info).encode()
        func_hash = hashlib.md5(func).hexdigest()
        self.assertEqual(func_hash, VALID_HASHES["_l10n_es_edi_get_invoices_info"])
