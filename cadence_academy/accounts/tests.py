from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Profile

User = get_user_model()

class AdminProfileTests(APITestCase):
    def setUp(self):
        # Create an admin user and log them in
        self.admin_user = User.objects.create_superuser(username='adminuser', email='adminuser@example.com', password='password123')
        self.client.login(username='adminuser', password='password123')

        # Create a normal user to test profile retrieval
        self.normal_user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        # Ensure the Profile creation reflects the current model structure
        self.normal_profile = Profile.objects.create(user=self.normal_user, bio='Test bio', address='123 Test St', country='Testland', date_of_birth='2000-01-01')

    def test_admin_retrieve_user_profile(self):
        # Using the assumption that 'admin-profile-detail' URL expects 'user_id' as a parameter
        url = reverse('admin-profile-detail', kwargs={'user_id': self.normal_user.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['address'], '123 Test St')
        self.assertEqual(response.data['country'], 'Testland')
        self.assertEqual(response.data['date_of_birth'], '2000-01-01')

# Create your tests here.
