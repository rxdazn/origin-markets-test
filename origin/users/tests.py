from django.test import TestCase
from rest_framework.authtoken.models import Token

from users.models import User


class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="joe@test.com")

    def test_user_has_api_key(self):
        """Ensures users have an api key after account creation"""
        try:
            api_key = Token.objects.get(user=self.user)
        except Token.DoesNotExist:
            api_key = None
        self.assertIsNotNone(api_key)
