# Design Document

Implementation choices are explained in this document.

## Implementation philosophy

This implementation aims to offer the required featureset described in
`README.md` in a user-friendly manner with a user flow similar to most web HTTP APIs such as:

- api token based auth
- REST-like API using standard HTTP verbs and status codes
- users being able to display GET endpoints results directly from their browsers

The code base is designed to be readable and maintainable, with a focus on
documentation ([DESIGN_DOC.md](DESIGN_DOC.md), [USER_GUIDE.md](USER_GUIDE.md))
as well as an extensive test suite (unit & integration tests).

The implementation itself is very basic but is laid out in a way to allow further
additions.

Software versions:
- Python 3.8.2
- Django 2.2.13
- Django Rest Framework 3.9.4

Extra external dependencies:

I tried avoiding external dependencies as they should be minimised for a test
exercise of this scope but these were worth adding as they greatly improve
code readability.

- requests==2.24.0: allows running http requests in a nice way
- responses==0.12.0: allows mocking server responses for http calls made with `requests`
- parameterized==0.7.4: allows [parameterizing](https://pypi.org/project/parameterized/) tests

Code is formatted using [black](https://github.com/psf/black) to avoid any
confusions or misuses when it comes to formatting.

Code changesets are broken down into small, clearly described commits, with
only one feature change per commit.  
If there was a code review process, one pull request would be submitted for each
commit as to ensure the patch would be easy to digest for the reviewer, speeding
up the submission/merge cycle, and increasing the odds of any changes requested by the
reviewer being quick to implement.

## Users

Users are implemented with a custom user class, and replaces the default Django
user class via the
[`AUTH_USER_MODEL`](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-AUTH_USER_MODEL`)
setting.

This is done despite the fact that the custom user class here doesn't add any
custom fields, as changing user models while a project is already running and has
existing migrations is a difficult and time-consuming task.
It is standard practise to replace the default user model from the very
beginning of a Django project.

### Authentication

Authentication uses Django Rest Framework's (DRF)
[TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
as token-based auth is standard in web APIs implementations.

API tokens are automatically created for users when they register their
accounts.
This is implemented via a `post_save` signal on the `User` model.

Users can see their API keys after logging in via `localhost:8080/login`.


#### Modifications

By default `TokenAuthentication` expects tokens to be passed via the
`Authorization` HTTP header, but for usability sake in this test exercise the
token will also be allowed to be passed as a query parameter named `api_key`.
This is done to allow fetching the API via a browser window rather than having
to use an HTTP client such as CURL or Postman in order to be able to pass custom
HTTP headers.


### Bonds

Bonds (`bonds.models.Bond`) entries are saved to the database with the following assumptions:

- all fields are mandatory
- none of the user-input fields seem to be serving as unique identifiers
- Model:  
```
    isin = models.CharField(max_length=20)

      The value for `isin` in README.md has a length of 12 but I increased the
      max limit if ever some of the input test values were a bit longer.

    size = models.IntegerField()

      Assumed this was simply an integer as there was no floating point in
      README.md.
      If this was a monetary value I would have this to be a `DecimalField`

    currency = models.CharField(max_length=3)

      max_length == 3 as we assume ISO currency codes will be used

    maturity = models.DateField()

      Only contains date details down to a day granularity (no minutes, seconds etc.)
      therefore it is a `DateField` rather than `DateTimeField`.
      As there is no Date type in the JSON specification I am assuming the
      requests to the API will pass `maturity` as  a string.
      Format and correctness will be done using strptime().
      Unsure whether maturity should allow values set in the past to I am
      allowing this behaviour.

    lei = models.CharField(max_length=40)

      The value for `lei` in README.md has a length of 20 but I increased the
      max limit if ever some of the input test values were a bit longer.

    legal_name = models.CharField(max_length=100)

      Assuming this is also a mandatory value, therefore if the name can't be
      looked up from the external gleif.org API, the Bond entry can't be
      created.

```

#### Bonds LEI data external lookup (leilookup.gleif.org API)

As requested in the instructions, using a Bond's LEI, its legal name is looked
up via the gleif.org API.

This adds an extra layer of complexity in terms of things to rely on;
our API user might send a perfectly valid Bond creation request but we could
have to generate an error if the gleif.org behaves unexpectedly.

The lookup code (bonds.services.get_legal_name) could be written in a much shorter way,
but in an effort to make the end API user friendly, I have decided to check many
of the possible failure points in order to be able to display useful error
messages; rather than showing a generic "Server error" or "Could not create
bond", it is more helpful for our API user to see messages such as "LEI server lookup
unavailable" or "LEI lookup server did not find matching record".
This is why that function can look a bit long/complex (I think it's definitely
worth it).

##### LEI Lookup testing

I made the tests hermetic meaning the gleif.org server isn't actually hit when
running the tests.
This is important to make the test suite reliable as we don't want our tests to
fail because a service we have no control over is down.

For this part all of the calls to gleif.org were mocked using
[responses](https://github.com/getsentry/responses).  
I tend to avoid mocking in general but this is useful to still test the expected
behaviour from external network calls.

Our tests handle a successful LEI match case, as well as the following error
cases (from `origin.constants`):

```
ERR_LEI_LOOKUP_UNREACHABLE = "LEI lookup server unreachable"
ERR_LEI_LOOKUP_ERROR_F = "LEI lookup server error [{status_code}]"
ERR_LEI_LOOKUP_INVALID_JSON_RESPONSE = "LEI lookup server invalid response format"
ERR_LEI_LOOKUP_NO_MATCH = "LEI lookup server did not find matching record"
ERR_LEI_LOOKUP_MULTIPLE_MATCHES = "LEI lookup server found multiple matching records"
ERR_LEI_LOOKUP_NO_LEGAL_NAME = "LEI lookup server did not return legal name data"
```

## API

The built API strictly only implements the endpoints described in README.md:

- POST /bonds/: to create a Bond
- GET /bonds/: to list a user's bonds, with an optional `legal_name` query
  parameter that filters Bonds with matching legal name values.
  I am assuming the `legal_name` is for exact strict matches.

This means no other verbs are supported; updating an entry is not possible
(as semantically we should be using the verb PUT), and fetching a single
entry is not possible either.
The payload and response formats also strictly match README.md, meaning some
features such as pagination are not possible, as they would modify the response
format by including metadata fields.

The decision to strictly adhere to the formats described in README.md was made
to support the case where the reviewer of this assignment would have a test
suite ready to run against the app.

## Further improvements

Below is a list of features that could be implemented to further improve the
app:


Code: 
- Add a currency library to make `Bond.currency` a text field with a `choice`
  whitelist value.  
  This was skipped as to avoid adding any unnecessary extra external dependencies for
  the scope of a small exercise, but would be useful in a production scenario.
- Add namespacing to URL names  
  Currently not needed but it would be useful to have namespaces or urls to be
  able to link/reverse view in a `'namespace:viewname'` format

User:
- Allow users to delete/regenerate API tokens. A simple security measure.

API:
- Add support for pagination. Not done in this version as to not divert from the
  format described in README.md
  Essential feature to support large collections without hammering the server
  while keeping decent server response times.
- Add rate limiting, to ensure decent server response time
- Add caching, to not always query the database, especially for GET endpoints
