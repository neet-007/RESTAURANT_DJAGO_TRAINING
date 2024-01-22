from django.test import TestCase
from django.test import LiveServerTestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from rest_framework.test import RequestsClient
from requests.auth import HTTPBasicAuth
from restaurent.models import MenuItem, Category
import json
# Create your tests here.
user_model = get_user_model()
class TestDeliveryCrewCase(LiveServerTestCase):
    def setUp(self):
        self.client = RequestsClient()
        self.client.headers.update({'x-test': 'true'})
        self.u1 = user_model.objects.create_superuser(email='manager@email.com', password='12345678')
        self.u2 = user_model.objects.create_user(email='user2@email.com', password='12345678')
        self.u3 = user_model.objects.create_user(email='user3@email.com', password='12345678')
        self.u4 = user_model.objects.create_user(email='user4@email.com', password='12345678')
        self.manager_group, created = Group.objects.get_or_create(name='manager')
        self.delviery_crew_group, created = Group.objects.get_or_create(name='delivery crew')
        self.manager_group.user_set.add(self.u1)
        self.delviery_crew_group.user_set.add(self.u2)

    def test_list(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/staff/delivery-crew/',headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_list_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('user2@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/staff/delivery-crew/',headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_create(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/delivery-crew/', {'email':'user3@email.com'}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 201)
        self.assertDictEqual(resp.json(), {'success':'user user3@email.com was added as a delivery crew'})

    def test_create_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('user2@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/delivery-crew/', {'email':'user3@email.com'}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_create_wrong_data(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/delivery-crew/', {'email':'use@email.com'}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 404)
        self.assertDictEqual(resp.json(), {'error':'user with provided credintials not found'})

    def test_delete(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.delete(self.live_server_url + f'/staff/delivery-crew/{self.u2.pk}', headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(resp.json(), {'success':f'user user2@email.com was removed from delivey crew'})

    def test_delete_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('user2@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.delete(self.live_server_url + f'/staff/delivery-crew/{self.u2.pk}', headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_delete_wrong_data(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.delete(self.live_server_url + f'/staff/delivery-crew/{self.u3.pk}',  headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 404)



class TestMenuItemCase(LiveServerTestCase):
    def setUp(self):
        self.client = RequestsClient()
        self.client.headers.update({'x-test': 'true'})
        self.u1 = user_model.objects.create_superuser(email='manager@email.com', password='12345678')
        self.u2 = user_model.objects.create_user(email='user2@email.com', password='12345678')
        self.manager_group, created = Group.objects.get_or_create(name='manager')
        self.manager_group.user_set.add(self.u1)
        self.categroy_1 = Category.objects.create(name='cat1')
        self.menu_item_1 = MenuItem.objects.create(name='item1', category=self.categroy_1, price=12.5)

    def test_list(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/staff/menu-item/',headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_list_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('user2@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.get(self.live_server_url + '/staff/menu-item/', headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_create_with_cat(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/menu-item/', json={'name':'test', 'category':{'name':'cat1'}, 'price':100}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 201)
        self.assertDictEqual(resp.json(), {'id': 2, 'featured': True, 'name':'test', 'category':{'id': 1, 'slug':'cat1', 'name':'cat1'}, 'price':"100.00"})

    def test_create_without_cat(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/menu-item/', json={'name':'test', 'category':{'name':'cat2'}, 'price':100}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 201)
        self.assertDictEqual(resp.json(), {'id': 2, 'featured': True, 'name':'test', 'category':{'id': 2, 'slug':'cat2', 'name':'cat2'}, 'price':"100.00"})

    def test_create_non_admin_user(self):
        self.client.auth = HTTPBasicAuth('user2@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/menu-item/', json={'name':'test', 'category':{'name':'cat2'}, 'price':100}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 403)

    def test_create_wrong_data(self):
        self.client.auth = HTTPBasicAuth('manager@email.com', '12345678')
        response = self.client.get(self.live_server_url + '/auth/get-csrf')
        csrftoken = response.cookies['csrftoken']
        resp = self.client.post(self.live_server_url + '/staff/menu-item/', json={'name':'test', 'category':{'name':['s']}, 'price':100}, headers={'X-CSRFToken': csrftoken})
        self.assertEqual(resp.status_code, 400)