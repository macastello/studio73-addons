# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestCommonPackageDimension


class TestPackageDimensionCompute(TestCommonPackageDimension):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_package_compute(self):
        self.package._compute_volume()
        self.assertEqual(
            12,
            self.package.volume,
            "Error, no se está calculando correctamente el volumen del paquete",
        )
        self.package.package_type_id = self.package_type
        self.package.height = 0  # Deberia usar el valor del tipo de paquete
        self.package._compute_volume()
        self.assertEqual(
            6,
            self.package.volume,
            "Error, no se está recalculando correctamente el volumen del paquete",
        )
