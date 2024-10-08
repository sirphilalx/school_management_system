from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date
from .models import Profile, CustomUser
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'newuser1',
            'email': 'newuser1@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser1')


class UserLoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='newuser1', email='newuser1@example.com', password='newpassword123')
        
    def test_login_user(self):
        url = reverse('login')
        data = {
            'username': 'newuser1',
            'password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        print("Response Data: ", response.data)  # For debugging purposes
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='newuser1', email='newuser1@example.com', password='newpassword123')
        self.profile, created = Profile.objects.get_or_create(user=self.user, defaults={'bio': 'New user bio'})
        if not created:
            self.profile.bio = 'New user bio'
            self.profile.save()
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_retrieve_own_profile(self):
        url = reverse('profile_detail', kwargs={'user_id': self.user.id})
        response = self.client.get(url, format='json')
        print(f'Response Data: {response.data}')  # Debugging line
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['bio'], 'New user bio')



class AdminProfileTests(APITestCase):

    def setUp(self):
        # Clean the database before running the test
        Profile.objects.all().delete()
        User.objects.all().delete()
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser2',
            email='adminuser2@example.com',
            password='adminpassword123',
            role='admin'
        )
        
        # Obtain the token for the admin user
        response = self.client.post(reverse('api_token_auth'), {
            'username': 'adminuser2',
            'password': 'adminpassword123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['token']
        
        # Use the token in the header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        # Create a normal user
        self.normal_user = User.objects.create_user(
            username='normaluser2',
            email='normaluser2@example.com',
            password='normalpassword123',
            role='user'
        )
        
        # Debug log to verify normal_user creation
        print(f"Created normal user: {self.normal_user}")

        # Use get_or_create to create or obtain the profile for the normal user
        self.normal_profile, created = Profile.objects.get_or_create(
            user=self.normal_user,
            defaults={
                'bio': 'Normal user bio',
                'address': '123 Normal St',
                'country': 'Normalland',
                'date_of_birth': date(2001, 1, 1)
            }
        )
        
        # Debug log to verify Profile creation status and details
        print(f"Profile creation status: {'Created' if created else 'Fetched existing'}")
        print(f"Profile details: {self.normal_profile}")

        if not created:
            # Ensure profile has accurate data if not created
            self.normal_profile.bio = 'Normal user bio'
            self.normal_profile.address = '123 Normal St'
            self.normal_profile.country = 'Normalland'
            self.normal_profile.date_of_birth = date(2001, 1, 1)
            self.normal_profile.save()

    def tearDown(self):
        # Clean up database after the test
        Profile.objects.all().delete()
        User.objects.all().delete()

    def test_admin_retrieve_user_profile(self):
        url = reverse('admin_profile_detail', kwargs={'user_id': self.normal_user.id})
        response = self.client.get(url, format='json')

        # Debug print the response data
        print(f"Response data: {response.data}")
        # Verify that the profile object has valid fields
        print(f"Normal profile date_of_birth: {self.normal_profile.date_of_birth}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], self.normal_profile.bio)
        self.assertEqual(response.data['address'], self.normal_profile.address)
        self.assertEqual(response.data['country'], self.normal_profile.country)

        # Check date_of_birth field
        if self.normal_profile.date_of_birth is not None:
            expected_date_of_birth = self.normal_profile.date_of_birth.strftime('%Y-%m-%d')
            print(f"Expected date_of_birth: {expected_date_of_birth}")
            self.assertEqual(response.data['date_of_birth'], expected_date_of_birth)
        else:
            self.fail("date_of_birth is None while it should be set.")


class PasswordChangeTests(APITestCase):
    def setUp(self):
        # Setup user and login
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='oldpassword123'
        )
        
        # Log in the user to get the token for authentication
        response = self.client.post(reverse('api_token_auth'), {
            'username': 'testuser',
            'password': 'oldpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['token']
        
        # Pass the token in the header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        
    def test_change_password(self):
        url = reverse('password_change')  # Corrected to match URL pattern
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456'
        }
        response = self.client.post(url, data, format='json')  # Ensure format is json
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='resetuser1', email='resetuser1@example.com', password='password123')
        
    def test_reset_password_request(self):
        url = reverse('password_reset_request')
        data = {'email': 'resetuser1@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reset_link', response.data)

    def test_password_reset_confirm(self):
        # Simulate password reset link
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        data = {'new_password': 'newpassword123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password has been reset successfully.')

        # Verify that the password has changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

class TeacherProfileTests(APITestCase):
    def setUp(self):
        # Create a teacher user
        self.teacher_user = User.objects.create_user(
            username='teacheruser1', 
            email='teacheruser1@example.com', 
            password='password123'
        )

        # Assign the role "TEACHER"
        self.teacher_user.role = 'TEACHER'
        self.teacher_user.save()

        # Ensure no existing profile interferes
        Profile.objects.filter(user=self.teacher_user).delete()

        # Create a Profile for the User
        self.teacher_profile, created = Profile.objects.get_or_create(
            user=self.teacher_user,
            defaults={
                'bio': 'Teacher bio',
                'address': '123 Teacher St',
                'country': 'Teacherland',
                'date_of_birth': date(1980, 3, 15),  # Ensure proper date object
            }
        )

        # Debug prints to verify setup
        print(f'Teacher Profile created: {self.teacher_profile}')
        if created:
            print(f'Teacher Profile creation - date_of_birth: {self.teacher_profile.date_of_birth}')
        else:
            print("Profile already existed and was fetched")

        # Log in the teacher user to get the token for authentication
        response = self.client.post(reverse('api_token_auth'), {
            'username': 'teacheruser1',
            'password': 'password123'
        })

        # Ensure the login is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher_token = response.data['token']

        # Pass the token in the header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token)

    def test_retrieve_teacher_profile(self):
        url = reverse('profile_detail', kwargs={'user_id': self.teacher_user.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Re-fetch the profile to ensure it reflects correct data
        self.teacher_profile.refresh_from_db()

        # Debug print to verify data after refresh
        print(f'Refreshed Teacher Profile date_of_birth: {self.teacher_profile.date_of_birth}')
        
        # Ensure the date_of_birth is not None
        self.assertIsNotNone(self.teacher_profile.date_of_birth, "date_of_birth should not be None")

        expected_date_of_birth = self.teacher_profile.date_of_birth.strftime('%Y-%m-%d')

        # Ensure to access 'profile' in the nested serializer response
        profile_data = response.data['profile']

        self.assertEqual(profile_data['bio'], self.teacher_profile.bio)
        self.assertEqual(profile_data['address'], self.teacher_profile.address)
        self.assertEqual(profile_data['country'], self.teacher_profile.country)
        self.assertEqual(profile_data['date_of_birth'], expected_date_of_birth)
        self.assertEqual(response.data['role'], self.teacher_user.role)


        # Additional assertions for user data
        self.assertEqual(response.data['username'], self.teacher_user.username)
        self.assertEqual(response.data['email'], self.teacher_user.email)

        # Debug print statements
        print(f'Response data: {response.data}')
        print(f'Expected date of birth: {expected_date_of_birth}')
        print(f'Teacher Role in Response: {response.data["role"]}')
        
        # Verifying additional internal state
        print(f'UserProfile in Response: {profile_data}')



class StudentProfileTests(APITestCase):
    def setUp(self):
        # Create a student user
        self.student_user = CustomUser.objects.create_user(
            username='studentuser1', 
            email='studentuser1@example.com', 
            password='password123',
            role='STUDENT'  # Ensure role is set correctly
        )

        # Ensure no existing profile interferes
        Profile.objects.filter(user=self.student_user).delete()

        # Create Profile for the User
        self.student_profile, created = Profile.objects.get_or_create(
            user=self.student_user,
            defaults={
                'bio': 'Student bio',
                'address': '123 Student St',
                'country': 'Studentland',
                'date_of_birth': date(2002, 5, 20),  # Ensure proper date object
            }
        )

        # Debug prints to verify setup
        print(f'Student Profile created: {self.student_profile}')
        print(f'Student Profile date_of_birth: {self.student_profile.date_of_birth}')

        # Log in the student user to get the token for authentication
        response = self.client.post(reverse('login'), {
            'username': 'studentuser1',
            'password': 'password123'
        })

        # Ensure the login is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_token = response.data['token']

        # Pass the token in the header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token)

    def test_retrieve_student_profile(self):
        url = reverse('profile_detail', kwargs={'user_id': self.student_user.id})  # Match the URL pattern name and pass user_id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Re-fetch the profile to ensure it reflects correct data
        self.student_profile.refresh_from_db()
        expected_date_of_birth = self.student_profile.date_of_birth.strftime('%Y-%m-%d')

        # Ensure to access 'profile' in the nested serializer response
        profile_data = response.data['profile']  # Accessing nested profile data

        self.assertEqual(profile_data['bio'], self.student_profile.bio)
        self.assertEqual(profile_data['address'], self.student_profile.address)
        self.assertEqual(profile_data['country'], self.student_profile.country)
        self.assertEqual(profile_data['date_of_birth'], expected_date_of_birth)
        
        # Since role is part of the User model, check it directly in the response.data
        self.assertEqual(response.data.get('role'), self.student_user.role)  # New assertion for role

        # Additional assertions for user data
        self.assertEqual(response.data['username'], self.student_user.username)
        self.assertEqual(response.data['email'], self.student_user.email)

        # Print statements to debug (Optional)
        print(f"Response data: {response.data}")
        print(f"Expected date of birth: {expected_date_of_birth}")