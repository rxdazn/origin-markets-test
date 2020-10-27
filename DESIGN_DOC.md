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
token will instead be passed as a query parameter named `key`.
This is done to allow fetching the API via a browser window rather than having
to use an HTTP client such as CURL or Postman in order to be able to pass custom
HTTP headers


## Further improvements

Below is a list of features that could be implemented to further improve the
app:


- Allow users to delete/regenerate API tokens. A simple security measure.
- Add a currency library to make `Bond.currency` a text field with a `choice`
  whitelist value.  
  This was skipped as to avoid adding any extra external dependencies, but would
  be useful in a production scenario.
- Add namespacing to URL names  
  Currently not needed but it would be useful to have namespaces or urls to be
  able to link/reverse view in a `'namespace:viewname'` format
