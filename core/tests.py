from django.test import TestCase
from django.contrib.auth.models import User

from . import models


class ClientTest(TestCase):
    def test_create_delete(self):
        # Creating
        models.Client.objects.create('test@test.com', 'qwerty123',
                                     'Test', 'Test')

        # Checking for user, client, account
        user = User.objects.filter(email='test@test.com').first()
        self.assertIsNotNone(user)

        client = user.client
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.account)
        self.assertEqual(client.account.balance, 0.0)

        client_pk = client.pk
        account_id = client.account.id

        # Deleting
        client.delete()

        # Checking for client, its account
        self.assertFalse(
            User.objects.filter(email='test@test.com').exists()
        )
        self.assertFalse(
            models.Client.objects.filter(pk=client_pk).exists()
        )
        self.assertFalse(
            models.Account.objects.filter(id=account_id).exists()
        )
