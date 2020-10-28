from django.test import TestCase
from parameterized import parameterized

from bonds.serializers import BondSerializer


class TestBondSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-03-27",
            "lei": "R0MUWSFPU8MPRO8K5P83",
            "legal_name": "AAA",
        }

    def test_valid_bond(self):
        serializer = BondSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    @parameterized.expand(["2020-03-03", "1992-03-30"])
    def test_maturity_valid_date_format(self, date):
        self.data["maturity"] = date
        serializer = BondSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    @parameterized.expand(
        [
            "92-03-30",  # year isn't 4-char long
            "2020-02-31",  # day does not exist
        ]
    )
    def test_maturity_invalid_date_format(self, date):
        self.data["maturity"] = date
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_isin_required(self):
        self.data["isin"] = ""
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_size_required(self):
        self.data["size"] = None
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_size_type_int(self):
        self.data["size"] = "ABC"
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    @parameterized.expand(
        [
            "",
            "E",
            "EU",
            "EURO",
        ]
    )
    def test_currency_length(self, currency):
        self.data["currency"] = currency
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_legal_name_required(self):
        self.data["legal_name"] = ""
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())

    def test_lei_required(self):
        self.data["lei"] = ""
        serializer = BondSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
