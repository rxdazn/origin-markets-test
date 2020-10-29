from rest_framework import authentication


class QueryStringTokenAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        if "api_key" in request.query_params:
            return self.authenticate_credentials(request.query_params.get("api_key"))
        else:
            return super().authenticate(request)
