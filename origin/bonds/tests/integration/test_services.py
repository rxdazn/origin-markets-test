import io
import json

from django.test import TestCase
import responses

from origin import constants
from bonds.tests.utilities import ResponsesMixin, mock_lei_lookup_response
from bonds.services import get_legal_name, LEILookupError


class TestLegalNameService(ResponsesMixin, TestCase):
    def test_lookup_success(self):
        server_response_dict = [
            {
                "LEI": {"$": "123"},
                "Entity": {
                    "LegalName": {
                        "$": "AAA BANK",
                    },
                },
            }
        ]
        server_response = json.dumps(server_response_dict)
        mock_lei_lookup_response("123", server_response)

        self.assertEqual(get_legal_name("123"), "AAA BANK")

    def test_lookup_server_unreachable(self):
        # only calls to testdomain.com will response - everything else will
        # produce a server error
        responses.add(responses.GET, "http://testdomain.com")

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(e_ctx.exception) == constants.ERR_LEI_LOOKUP_UNREACHABLE

    def test_lookup_invalid_response_no_json(self):
        server_response = "non-json text here"
        mock_lei_lookup_response("123", server_response)

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(e_ctx.exception) == constants.ERR_LEI_LOOKUP_INVALID_JSON_RESPONSE

    def test_lookup_bad_response_status(self):
        mock_lei_lookup_response("123", "Bad request", status_code=400)

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(
            e_ctx.exception == constants.ERR_LEI_LOOKUP_ERROR_F.format(status_code=400)
        )

    def test_lookup_no_match(self):
        mock_lei_lookup_response("123", "[]")

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(e_ctx.exception) == constants.ERR_LEI_LOOKUP_NO_MATCH

    def test_lookup_too_many_matches(self):
        mock_lei_lookup_response("123", "[{}, {}]")

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(e_ctx.exception) == constants.ERR_LEI_LOOKUP_MULTIPLE_MATCHES

    def test_lookup_no_legal_name(self):
        """server responds successfully, with only one match, but does not include a LegalName entry where expected"""
        server_response_dict = [
            {
                "LEI": {"$": "123"},
                "Entity": {},
            }
        ]
        server_response = json.dumps(server_response_dict)
        mock_lei_lookup_response("123", server_response)

        with self.assertRaises(LEILookupError) as e_ctx:
            get_legal_name("123")
        assert str(e_ctx.exception) == constants.ERR_LEI_LOOKUP_NO_LEGAL_NAME
