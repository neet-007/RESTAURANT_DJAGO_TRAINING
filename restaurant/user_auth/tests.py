from django.test import TestCase
from django.test import LiveServerTestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from rest_framework.test import RequestsClient
from requests.auth import HTTPBasicAuth
# Create your tests here.
class TestManagerTestCase(LiveServerTestCase):
    def setUp(self):
        self.client = RequestsClient()
        self.client.headers.update({'x-test': 'true'})
        self.u1 = get_user_model().objects.create_superuser(email='test@email.com', password='test12345678')
        self.u2 = get_user_model().objects.create_user(email='manager@email.com', password='test12345678')
        manager_group, created = Group.objects.get_or_create(name='manager')
        manager_group.user_set.add(self.u1)

    def test_list(self):
        self.client.auth = HTTPBasicAuth('test@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/auth/managers/',headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_list_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/auth/managers/',headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_create(self):
        self.client.auth = HTTPBasicAuth('test@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/auth/managers/', {'email':self.u2.email},headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(resp.json(), {'success':'user manager@email.com is now a manager'})

    def test_create_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/auth/managers/', {'email':self.u2.email},headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_destroy(self):
        manager_group, created = Group.objects.get_or_create(name='manager')
        manager_group.user_set.add(self.u2)
        self.client.auth = HTTPBasicAuth('test@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.delete(self.live_server_url + f'/auth/managers/{self.u2.pk}/', headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)

    def test_destroy_non_admin_user(self):
        manager_group, created = Group.objects.get_or_create(name='manager')
        manager_group.user_set.add(self.u2)
        self.client.auth = HTTPBasicAuth('manager@email.com', 'test12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.delete(self.live_server_url + f'/auth/managers/{self.u2.pk}/', headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)