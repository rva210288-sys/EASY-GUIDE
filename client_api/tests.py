from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate

from core import models
from . import views


class LanguageTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_list(self):
        view = views.LanguageViewSet.as_view({'get': 'list'})
        request = self.factory.get('/client-api/languages/')
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

        lang_codes = {lang['code'] for lang in response.data}
        self.assertTrue('en' in lang_codes)

    def test_retrieve(self):
        view = views.LanguageViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('/client-api/languages/en/')
        response = view(request, pk='en')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
        self.assertEqual(response.data['code'], 'en')


class ClientTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        client = models.Client.objects.create('test@test.com', 'qwerty123', 'Test', 'Test')
        self.user = client.user
        self.uid = client.user.id

    def test_list(self):
        view = views.ClientViewSet.as_view({'get': 'list'})
        request = self.factory.get('/client-api/clients/')
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
        self.assertEqual(len(response.data), 1)
        client = response.data[0]
        self.assertEqual(client['user']['email'], 'test@test.com')

    def test_retrieve(self):
        view = views.ClientViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'/client-api/clients/{self.uid}/')
        response = view(request, pk=self.uid)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
        self.assertEqual(response.data['user']['id'], self.uid)
        self.assertEqual(response.data['user']['email'], 'test@test.com')
        self.assertIsNone(response.data['account'])
        self.assertIsNone(response.data['guide_profile'])

        force_authenticate(request, user=self.user)
        response = view(request, pk=self.uid)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['account'])
        self.assertIsNotNone(response.data['guide_profile'])

    def test_create(self):
        view = views.ClientViewSet.as_view({'post': 'create'})
        data = {
            'email': 'my@mail.com',
            'password': 'qwerty123',
            'first_name': 'My',
            'last_name': 'Mail',
        }
        request = self.factory.post('/client-api/clients/', data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data)
        self.assertTrue(response.data['user'])
        self.assertTrue(response.data['user']['id'])
        self.assertEqual(response.data['user']['email'], 'my@mail.com')
        self.assertEqual(response.data['user']['last_name'], 'Mail')

    def test_update(self):
        view = views.ClientViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'/client-api/clients/{self.uid}/')
        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 200)
        data = response.data

        data['last_name'] = 'Test2'
        data['about'] = 'Some text'
        data['driving_experience'] = 3

        view = views.ClientViewSet.as_view({'put': 'update'})
        request = self.factory.put(f'/client-api/clients/{self.uid}/', data, format='json')

        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 403)

        force_authenticate(request, user=self.user)
        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 200)

        client = models.Client.objects.get(pk=self.uid)
        self.assertEqual(client.last_name, 'Test2')
        self.assertEqual(client.about, 'Some text')
        self.assertEqual(client.driving_experience, 3)

    def test_partial_update(self):
        data = {
            'last_name': 'Test2',
            'about': 'Some text',
            'driving_experience': 3,
        }

        view = views.ClientViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch('/client-api/clients/', data, format='json')

        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 403)

        force_authenticate(request, user=self.user)
        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 200)

        client = models.Client.objects.get(pk=self.uid)
        self.assertEqual(client.last_name, 'Test2')
        self.assertEqual(client.about, 'Some text')
        self.assertEqual(client.driving_experience, 3)

    def test_delete(self):
        view = views.ClientViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'/client-api/clients/{self.uid}/')
        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 403)

        force_authenticate(request, user=self.user)
        response = view(request, pk=self.uid)
        self.assertEqual(response.status_code, 204)

        with self.assertRaises(models.Client.DoesNotExist):
            models.Client.objects.get(pk=self.uid)

    def test_guide_profile_create_delete(self):
        # Creating
        view = views.GuideProfileViewSet.as_view({'post': 'create'})
        data = {}
        request = self.factory.post('/client-api/guide-profiles/', data, format='json')

        response = view(request)
        self.assertEqual(response.status_code, 403)

        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            models.GuideProfile.objects.filter(client__pk=self.uid).exists()
        )

        guide_profile_id = response.data['id']

        # Deleting
        view = views.GuideProfileViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete('/client-api/guide-profiles/')

        response = view(request, pk=guide_profile_id)
        self.assertEqual(response.status_code, 403)

        force_authenticate(request, user=self.user)
        response = view(request, pk=guide_profile_id)
        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            models.GuideProfile.objects.filter(client__pk=self.uid).exists()
        )
