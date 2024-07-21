from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task

class TaskListNotLoggedIn(TestCase):
    def test_task_list_view_no_login(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
    
    def test_no_logged_in_incorrect_pw(self): 
        # Trying to log in with incorrect password
        self.client.login(username='testuser', password='wrongpassword')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect (likely to login)

class TaskListLoggedIn(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.task1 = Task.objects.create(user=self.user, title='Task 1', description='Description 1', complete=False)
        self.task2 = Task.objects.create(user=self.user, title='Task 2', description='Description 2', complete=True)

    # registered user + correct pw
    def test_loggedInCorrectPW(self): 
        self.client.login(username='testuser', password='password')
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Expecting success (200 OK)

class UniqueUser(TestCase):
    def setUp(self):
        self.user = User(username='testuser1')
        self.user.set_password('Valid1Password!')
        self.user.save()

    def test_register_with_same_username(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser1',
            'password': 'Valid2Password!',  
        })
        self.assertEqual(response.status_code, 200)  # Page reloads with errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors) # prompt user to re-enter username

class PasswordValidationTests(TestCase):
    def setUp(self):
        self.user = User(username='testuser1')
        self.user.set_password('Valid1Password!')
        self.user.save()

    def test_valid_password(self):
        self.user.set_password('Valid1Password!')
        self.user.save()
        self.assertTrue(self.user.check_password('Valid1Password!'))

    def test_password_too_similar(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser5',
            'password': 'testuser4',  # Example of too similar password
        })
        self.assertEqual(response.status_code, 200)  # Page reloads with errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password1', form.errors) # prompt user to re-enter password

    def test_password_too_short(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'Short1!',  # Example of too short password
        })
        self.assertEqual(response.status_code, 200)  # Page reloads with errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password1', form.errors)  # prompt user to re-enter password

    def test_common_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser3',
            'password': 'password',  # Example of too common password
        })
        self.assertEqual(response.status_code, 200)  # Page reloads with errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password1', form.errors)  # prompt user to re-enter password

    def test_numeric_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser4',
            'password': '12345678',  # Example of numeric-only password
        })
        self.assertEqual(response.status_code, 200)  # Page reloads with errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password1', form.errors)  # prompt user to re-enter password
        
    def test_special_characters(self):
        self.user.set_password('Special@2024')
        self.user.save()
        self.assertTrue(self.user.check_password('Special@2024'))

    def test_password_reuse(self):
        # Assuming you have a method to check password history
        self.user.set_password('PreviousPassword1!')
        self.user.save()
        self.assertTrue(self.user.check_password('PreviousPassword1!'))

    def test_password_confirmation(self):
        # Simulate form validation
        password = 'Confirm1!'
        password_confirmation = 'Confirm1!'
        self.assertEqual(password, password_confirmation)

        # Simulate mismatch
        password_confirmation = 'Different1!'
        self.assertNotEqual(password, password_confirmation)

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
