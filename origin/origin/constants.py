# LEI (gleif.org) lookup server errors

LEI_LOOKUP_URL_F = "https://leilookup.gleif.org/api/v2/leirecords?lei={lei}"

ERR_LEI_LOOKUP_UNREACHABLE = "LEI lookup server unreachable"
ERR_LEI_LOOKUP_ERROR_F = "LEI lookup server error [{status_code}]"
ERR_LEI_LOOKUP_INVALID_JSON_RESPONSE = "LEI lookup server invalid response format"
ERR_LEI_LOOKUP_NO_MATCH = "LEI lookup server did not find matching record"
ERR_LEI_LOOKUP_MULTIPLE_MATCHES = "LEI lookup server found multiple matching records"
ERR_LEI_LOOKUP_NO_LEGAL_NAME = "LEI lookup server did not return legal name data"
