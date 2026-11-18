import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['USE_SQLITE'] = 'True'
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.authentication.models import User
from apps.organizations.models import Organization, Membership, Project

class AuthAndRBACTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Tenant 1 Admin
        self.user1 = User.objects.create_user(
            email='alice@tenant1.com',
            password='SecurePassword123!',
            first_name='Alice',
            role=User.Role.ORG_ADMIN
        )
        self.org1 = Organization.objects.create(name='Tenant 1 Org', slug='tenant-1')
        Membership.objects.create(user=self.user1, organization=self.org1, role=Membership.OrgRole.ADMIN)
        self.user1.current_organization = self.org1
        self.user1.save()

        # Create Tenant 2 Admin
        self.user2 = User.objects.create_user(
            email='bob@tenant2.com',
            password='SecurePassword123!',
            first_name='Bob',
            role=User.Role.ORG_ADMIN
        )
        self.org2 = Organization.objects.create(name='Tenant 2 Org', slug='tenant-2')
        Membership.objects.create(user=self.user2, organization=self.org2, role=Membership.OrgRole.ADMIN)
        self.user2.current_organization = self.org2
        self.user2.save()

        # Create Project in Tenant 1
        self.project1 = Project.objects.create(organization=self.org1, name='Tenant 1 Core App')

    def test_user_registration_creates_workspace(self):
        payload = {
            'email': 'charlie@company.com',
            'password': 'StrongPassword123!',
            'first_name': 'Charlie',
            'role': User.Role.DEVELOPER,
            'organization_name': "Charlie's Team"
        }
        response = self.client.post('/api/v1/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Verify default organization and admin membership created
        new_user = User.objects.get(email='charlie@company.com')
        self.assertIsNotNone(new_user.current_organization)
        self.assertEqual(new_user.current_organization.name, "Charlie's Team")
        self.assertTrue(Membership.objects.filter(user=new_user, organization=new_user.current_organization).exists())

    def test_jwt_token_login_and_claims(self):
        payload = {
            'email': 'alice@tenant1.com',
            'password': 'SecurePassword123!'
        }
        response = self.client.post('/api/v1/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'alice@tenant1.com')
        self.assertEqual(response.data['user']['current_organization']['name'], 'Tenant 1 Org')

    def test_tenant_isolation_projects(self):
        # Authenticate as Bob (Tenant 2)
        self.client.force_authenticate(user=self.user2)

        # Attempt to retrieve projects
        response = self.client.get('/api/v1/organizations/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Bob must NOT see Alice's project (Tenant 1 Core App)
        project_ids = [p['id'] for p in response.data.get('results', response.data)]
        self.assertNotIn(str(self.project1.id), project_ids)

    def test_cross_tenant_object_access_blocked(self):
        # Authenticate as Bob (Tenant 2) and try to access Tenant 1 Org details directly
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/v1/organizations/{self.org1.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_member_invite_blocked(self):
        # Create a Developer in Tenant 1 (should NOT be able to invite members)
        dev_user = User.objects.create_user(
            email='dev@tenant1.com',
            password='SecurePassword123!',
            role=User.Role.DEVELOPER
        )
        Membership.objects.create(user=dev_user, organization=self.org1, role=Membership.OrgRole.DEVELOPER)
        dev_user.current_organization = self.org1
        dev_user.save()

        self.client.force_authenticate(user=dev_user)
        payload = {'email': 'hacker@tenant1.com', 'role': 'admin'}
        response = self.client.post(f'/api/v1/organizations/{self.org1.id}/members/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
