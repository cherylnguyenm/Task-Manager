import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from base.models import Task

class TaskListNotLoggedIn(TestCase):
    def test_task_list_view_no_login(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect

class TaskListLoggedIn(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.task1 = Task.objects.create(user=self.user, title='Task 1', description='Description 1', complete=False)
        self.task2 = Task.objects.create(user=self.user, title='Task 2', description='Description 2', complete=True)

    # registered user + correct pw
    def loggedInCorrectPW(self): 
        self.client.login(username='testuser', password='password')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Expecting success (200 OK)

    registered user + incorrect pw
    def loggedInIncorrectPW(self): 
        self.client.login(username='testuser', password='wrongpassword')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Expecting 401 Unauthorized

class TaskDetailTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.task = Task.objects.create(title='Task 1', user=self.user)

    def test_task_detail_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task_info'], self.task)

class TaskCreateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_task_create_view(self):
        self.client.login(username='testuser', password='password')
        new_task_data = {
            'title': 'New Task',
            'description': 'Description of new task',
            'complete': False,
        }
        response = self.client.post(reverse('task-create'), data=new_task_data)
        self.assertEqual(response.status_code, 302)  # Redirects to task list on success

        # Verify the task was created
        created_task = Task.objects.get(title='New Task')
        self.assertEqual(created_task.description, 'Description of new task')

class TaskUpdateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.task = Task.objects.create(title='Task 1', user=self.user)

    def test_task_update_view(self):
        self.client.login(username='testuser', password='password')
        updated_task_data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'complete': True,
        }
        response = self.client.post(reverse('task-update', args=[self.task.id]), data=updated_task_data)
        self.assertEqual(response.status_code, 302)  # Redirects to task list on success

        # Verify the task was updated
        updated_task = Task.objects.get(pk=self.task.id)
        self.assertEqual(updated_task.title, 'Updated Task')
        self.assertEqual(updated_task.description, 'Updated description')
        self.assertTrue(updated_task.complete)

class TaskDeleteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.task = Task.objects.create(title='Task 1', user=self.user)

    def test_task_delete_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('task-delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to task list on success

        # Verify the task was deleted
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=self.task.id)

    def test_task_delete_view_no_login(self):
        response = self.client.post(reverse('task-delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to login page if not logged in

if __name__ == '__main__':
    unittest.main()
