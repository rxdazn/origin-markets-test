import responses

from origin import constants


class ResponsesMixin:
    """
    Mixin to enable `responses` on each method of a test classs

    This allows mocking out any `requests` responses.
    """

    def setUp(self):
        responses.start()

    def tearDown(self):
        super().tearDown()
        responses.stop()
        responses.reset()


def mock_lei_lookup_response(
    lei, body, content_type="application/json", status_code=200
):
    responses.add(
        responses.GET,
        constants.LEI_LOOKUP_URL_F.format(lei=lei),
        body=body,
        content_type=content_type,
        status=status_code,
    )
