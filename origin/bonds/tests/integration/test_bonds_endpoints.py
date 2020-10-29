from unittest import mock

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


from origin import constants
from bonds.serializers import BondSerializer
from bonds.services import LEILookupError


class TestAuthToken(APITestCase):
    """Ensures api tokens can be passed via headers as well as query parameters"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="rob")

    def tearDown(self):
        super().tearDown()
        self.user.delete()

    def test_auth_token_header_missing(self):
        response = self.client.get("/bonds/")
        self.assertEquals(response.status_code, 401)

    def test_auth_token_header_success(self):
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get("/bonds/")
        self.assertEquals(response.status_code, 200)

    def test_auth_token_query_parameter(self):
        token = Token.objects.get(user=self.user)
        response = self.client.get(f"/bonds/?api_key={token.key}")
        self.assertEquals(response.status_code, 200)

    def test_auth_invalid_token(self):
        response = self.client.get(f"/bonds/?api_key=invalid")
        self.assertEquals(response.status_code, 401)


class TestCreateBonds(APITestCase):
    def setUp(self):
        self.bond_data = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-03-27",
            "lei": "R0M123",
        }
        self.user = get_user_model().objects.create_user(username="rob")
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def tearDown(self):
        self.user.delete()
        super().tearDown()

    @mock.patch("bonds.models.get_legal_name")
    def test_create_success(self, lei_lookup_mock):
        lei_lookup_mock.return_value = "BNP PARIBAS"

        response = self.client.post("/bonds/", self.bond_data, format="json")

        lei_lookup_mock.assert_called_once()
        self.assertEquals(response.status_code, 201)

    @mock.patch("bonds.models.get_legal_name")
    def test_lei_lookup_service_error(self, lei_lookup_mock):
        """Ensures error messages generated while using the LEI lookup service are shown to the end user"""
        lei_lookup_mock.side_effect = LEILookupError(constants.ERR_LEI_LOOKUP_NO_MATCH)

        response = self.client.post("/bonds/", self.bond_data, format="json")

        lei_lookup_mock.assert_called_once()
        self.assertEquals(response.status_code, 500)
        self.assertTrue("lei_lookup_error" in response.json())
        self.assertEquals(
            response.json()["lei_lookup_error"], constants.ERR_LEI_LOOKUP_NO_MATCH
        )

    def test_serializer_mandatory_fields(self):
        """Ensures missing mandatory fields are shown to the API user"""
        expected_mandatory_fields = set(["isin", "size", "currency", "maturity", "lei"])

        response = self.client.post("/bonds/", {}, format="json")
        response_json = response.json()

        self.assertEquals(response.status_code, 400)
        self.assertEquals(expected_mandatory_fields, response_json.keys())
        for field_name in expected_mandatory_fields:
            self.assertEquals(response_json[field_name], ["This field is required."])

    def test_serializer_validation(self):
        """Ensures validation errors are shown to the API user"""

        self.bond_data["currency"] = "EURO"
        response = self.client.post("/bonds/", self.bond_data, format="json")
        response_json = response.json()

        self.assertEquals(response.status_code, 400)
        self.assertEquals(len(response_json.keys()), 1)
        self.assertEquals(
            response_json["currency"],
            ["Ensure this field has no more than 3 characters."],
        )


class TestListBonds(APITestCase):
    def setUp(self):
        self.bond_data = {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-03-27",
            "lei": "R0M123",
        }
        self.user = get_user_model().objects.create_user(username="rob")
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def tearDown(self):
        self.user.delete()
        super().tearDown()

    @mock.patch("bonds.models.get_legal_name")
    def test_list_success(self, lei_lookup_mock):
        lei_lookup_mock.return_value = "BNP PARIBAS"
        self.client.post("/bonds/", self.bond_data, format="json")

        response = self.client.get("/bonds/")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.json(),
            [
                {
                    "legal_name": "BNP PARIBAS",
                    "maturity": "2025-03-27",
                    "currency": "EUR",
                    "isin": "FR0000131104",
                    "size": 100000000,
                    "lei": "R0M123",
                }
            ],
        )

    @mock.patch("bonds.models.get_legal_name")
    def test_list_multiple(self, lei_lookup_mock):
        """Ensures all entries are listed if multiple are created"""

        lei_lookup_mock.return_value = "BNP PARIBAS"
        self.client.post("/bonds/", self.bond_data, format="json")

        lei_lookup_mock.return_value = "BNP PARIBAS 2"
        self.client.post("/bonds/", self.bond_data, format="json")

        response = self.client.get("/bonds/")
        response_json = response.json()

        self.assertEquals(len(response_json), 2)
        self.assertEquals(response_json[0]["legal_name"], "BNP PARIBAS")
        self.assertEquals(response_json[1]["legal_name"], "BNP PARIBAS 2")

    @mock.patch("bonds.models.get_legal_name")
    def test_list_filter_exact_legal_name(self, lei_lookup_mock):
        """Ensures `legal_name` query parameter is supported and returns strict exact matches only"""
        lei_lookup_mock.return_value = "BNP"
        self.client.post("/bonds/", self.bond_data, format="json")

        lei_lookup_mock.return_value = "BNP3"
        self.client.post("/bonds/", self.bond_data, format="json")

        response = self.client.get("/bonds/?legal_name=NOTHING_MATCHING")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()), 0)

        response = self.client.get("/bonds/?legal_name=BNP")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()), 1)

        response = self.client.get("/bonds/?legal_name=BNP3")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()), 1)

    @mock.patch("bonds.models.get_legal_name")
    def test_list_only_user_created_entries(self, lei_lookup_mock):
        """Ensures the list endpoint only shows Bonds created by the authenticated user"""
        lei_lookup_mock.return_value = "BNP PARIBAS"

        self.client.post("/bonds/", self.bond_data, format="json")

        response = self.client.get("/bonds/")
        self.assertEquals(len(response.json()), 1)

        user2 = get_user_model().objects.create_user(username="pat")
        token2 = Token.objects.get(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token2.key}")
        response = self.client.get("/bonds/")

        self.assertEquals(len(response.json()), 0)
