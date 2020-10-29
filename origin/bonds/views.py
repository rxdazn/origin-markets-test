from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets

from origin.authentication import QueryStringTokenAuthentication
from bonds.models import Bond
from bonds.services import LEILookupError
from bonds.serializers import BondSerializer


class BondViewSet(viewsets.ViewSet):

    authentication_classes = [QueryStringTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def create(self, request):
        serializer = BondSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except LEILookupError as e:
                return Response(
                    {"lei_lookup_error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        serializer = BondSerializer(Bond.objects.filter(user=request.user), many=True)
        return Response(serializer.data)
