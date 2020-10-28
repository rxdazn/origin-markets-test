from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
import responses
from unittest import mock

from bonds.models import Bond
from bonds.tests.utilities import ResponsesMixin, mock_lei_lookup_response


class TestBondLegalName(ResponsesMixin, TestCase):
    """Ensures Bond.legal_name is set automatically when the model is saved"""

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username="rob")

    def tearDown(self):
        super().tearDown()
        self.user.delete()

    @mock.patch("bonds.models.get_legal_name")
    def test_legal_name_set(self, get_legal_name_mock):
        get_legal_name_mock.return_value = "BNP PARIBAS"
        bond = Bond.objects.create(
            isin="FR0000131104",
            size=100000000,
            currency="EUR",
            maturity=date.today(),
            lei="R0MUWSFPU8MPRO8K5P83",
            user=self.user,
        )

        get_legal_name_mock.assert_called_once()
        self.assertEquals(bond.legal_name, "BNP PARIBAS")

    @mock.patch("bonds.models.get_legal_name")
    def test_legal_name_updated(self, get_legal_name_mock):
        get_legal_name_mock.return_value = "BNP PARIBAS"
        bond = Bond.objects.create(
            isin="FR0000131104",
            size=100000000,
            currency="EUR",
            maturity=date.today(),
            lei="R0MUWSFPU8MPRO8K5P83",
            user=self.user,
        )

        get_legal_name_mock.assert_called_once()
        self.assertEquals(bond.legal_name, "BNP PARIBAS")

        get_legal_name_mock.return_value = "BNP PARIBAS (UPDATED)"
        bond.save()
        self.assertEquals(get_legal_name_mock.call_count, 2)
        self.assertEquals(bond.legal_name, "BNP PARIBAS (UPDATED)")
