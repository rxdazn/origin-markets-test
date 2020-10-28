import json

import requests

from origin import constants


class LEILookupError(Exception):
    pass


def get_legal_name(lei):
    """
    Fetches a record by LEI to get a matching legal name.

    gleif.org API returns data in the following format:
    ```
    [
      {
          "LEI": {
                "$": "4469000001AVO26P9X86"
          },
          "Entity": {
              "LegalName": {
                  "@xml:lang": "es",
                  "$": "ASOCIACION MEXICANA DE ESTANDARES PARA EL COMERCIO ELECTRONICO AC"
              },
          },
          ....
      }
    ]
    ```

    Raises:
      LEILookupError: when LEI data could not be fetched successfully.
    """
    url = constants.LEI_LOOKUP_URL_F.format(lei=lei)
    try:
        response = requests.get(url)
        if not response.status_code == requests.codes.ok:
            raise LEILookupError(
                constants.ERR_LEI_LOOKUP_ERROR_F.format(
                    status_code=response.status_code
                )
            )
        try:
            lei_data = response.json()
            assert isinstance(lei_data, list)
        except (ValueError, AssertionError):
            # server didn't return valid response (not JSON, or incorrectly formatted)
            raise LEILookupError(constants.ERR_LEI_LOOKUP_INVALID_JSON_RESPONSE)
        if len(lei_data) == 0:
            raise LEILookupError(constants.ERR_LEI_LOOKUP_NO_MATCH)
        if len(lei_data) > 1:
            raise LEILookupError(constants.ERR_LEI_LOOKUP_MULTIPLE_MATCHES)
        try:
            return lei_data[0]["Entity"]["LegalName"]["$"]
        except (IndexError, KeyError):
            raise LEILookupError(constants.ERR_LEI_LOOKUP_NO_LEGAL_NAME)
    except requests.exceptions.ConnectionError:
        raise LEILookupError(constants.ERR_LEI_LOOKUP_UNREACHABLE)
