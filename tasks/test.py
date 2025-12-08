from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
import datetime

User = get_user_model()

class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass12345')
        self.client.force_authenticate(user=self.user)

    def test_create_task_due_date_validation(self):
        url = reverse('task-list')
        past_date = (timezone.now() - datetime.timedelta(days=1)).isoformat()
        data = {
            'title': 'Test',
            'description': 'desc',
            'due_date': past_date,
            'priority': 'low',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_task_and_block_edit(self):
        # create a valid future due date
        future = (timezone.now() + datetime.timedelta(days=3)).isoformat()
        resp = self.client.post(reverse('task-list'), {
            'title': 'T1', 'due_date': future, 'priority': 'medium'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task_id = resp.data['id']

        # mark completed
        resp2 = self.client.post(reverse('task-set-status', args=[task_id]), {'status': 'completed'}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data['status'], 'completed')
        self.assertIsNotNone(resp2.data['completed_at'])

        # attempt to edit title while completed -> should fail
        resp3 = self.client.patch(reverse('task-detail', args=[task_id]), {'title': 'New title'}, format='json')
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)
