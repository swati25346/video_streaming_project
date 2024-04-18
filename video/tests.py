from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Video

class VideoAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='adm', password='123')
        self.client.login(username='adm', password='123')
        self.video = Video.objects.create(name='vid', url='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', user=self.user)

    def test_register_api(self):
        response = self.client.post(reverse('register'), {'username': 'adm', 'password': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='adm').exists())

    def test_user_login_api(self):
        response = self.client.post(reverse('login'), {'username': 'adm', 'password': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['user_id'])

    def test_user_logout_api(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)

    def test_upload_video_api(self):
        response = self.client.post(reverse('upload_video'), {'name': 'New Video', 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Video.objects.filter(name='New Video').exists())

    

    def test_delete_video_api(self):
        response = self.client.post(reverse('delete_video', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())

    

    

    def test_watch_video_api(self):
        response = self.client.get(reverse('watch_video', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)

    def tearDown(self):
        self.client.logout()
