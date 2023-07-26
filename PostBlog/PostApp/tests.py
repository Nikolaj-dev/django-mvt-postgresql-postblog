from django.test import TestCase
from .models import Post, PostComment, Profile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
import os
from django.urls import reverse


BASE_DIR = Path(__file__).resolve().parent.parent
image1 = SimpleUploadedFile(
    name='lake.jpg',
    content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'), 'rb').read(),
    content_type='image/jpeg'
)
image2 = SimpleUploadedFile(
    name='ocean.jpg',
    content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpg'), 'rb').read(),
    content_type='image/jpeg'
)
image3 = SimpleUploadedFile(
    name='tree.jpg',
    content=open(os.path.join(BASE_DIR, 'static/test_pics/tree.jpg'), 'rb').read(),
    content_type='image/jpeg'
)


# class LoginViewTest(TestCase):
#     def setUp(self):
#         self.username = 'testUser'
#         self.password = 'testPass'
#         self.user = User.objects.create_user(
#             username=self.username,
#             password=self.password
#         )
#
#     def test_login_view_with_valid_credentials(self):
#         response = self.client.post(reverse('login'), {
#             'username': self.username,
#             'password': self.password
#         })
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(response.wsgi_request.user.is_authenticated)
#
#     def test_login_view_with_invalid_credentials(self):
#         response = self.client.post(reverse('login'), {
#             'username': self.username,
#             'password': 'incorrectpassword'
#         })
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(response.wsgi_request.user.is_authenticated)
#
#
# class SignUpViewTest(TestCase):
#     def test_signup_view_with_valid_credentials(self):
#         response = self.client.post(
#             reverse('sign_up'),
#             {
#                 'username': 'testUser',
#                 'password1': 'testPass',
#                 'password2': 'testPass',
#                 'image': image1,
#                 'nickname': 'testNickname',
#                 'email': 'testEmail@gmail.com',
#             }
#         )
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(User.objects.count(), 1)
#         self.assertTrue(response.wsgi_request.user.is_authenticated)
#
#     def test_signup_view_with_invalid_credentials(self):
#         response = self.client.post(
#             reverse('sign_up'),
#             {
#                 'username': 'wrongTestUser',
#                 'password1': 'testPass1',
#                 'password2': 'testPass2',
#                 'image': image2,
#                 'nickname': 'wrongTestNickname',
#                 'email': 'wrongTestEmail@gmail.com',
#             }
#         )
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(User.objects.count(), 0)
#         self.assertTrue(response.wsgi_request.user.is_anonymous)
#
#
# class AllPostsViewTest(TestCase):
#     def test_get_method(self):
#         response = self.client.get(reverse('posts'))
#         self.assertEqual(response.status_code, 200)
#
#
# class DetailedPostViewsCRUDTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testAdmin',
#             password='testPassword'
#         )
#         self.post_for_getting = Post.objects.create(
#             title='testPost1',
#             body='testBody',
#             author=self.user,
#             image=image2,
#         )
#         self.post_for_posting = Post.objects.create(
#             title='testPost2',
#             body='testBody',
#             author=self.user,
#             image=image3,
#         )
#
#         self.post_for_getting_url = reverse('post', kwargs={'slug': self.post_for_getting.slug})
#         self.post_for_posting_url = reverse('post', kwargs={'slug': self.post_for_posting.slug})
#         self.client.login(username='testAdmin', password='testPassword')
#
#     def test_get_method(self):
#         response = self.client.get(self.post_for_getting_url)
#         self.assertTrue(response.status_code, 200)
#
#     def test_valid_post_method(self):
#         response = self.client.post(path=self.post_for_posting_url, data={'comment': 'Nice Post!'})
#         self.assertEqual(response.status_code, 302)
#
#     def test_invalid_post_method(self):
#         response = self.client.post(path=self.post_for_posting_url, data={'comment': ''})
#         self.assertEqual(response.status_code, 302)
#         if PostComment.objects.all():
#             comments = False
#             self.assertTrue(comments)
#
#     def test_valid_update_method(self):
#         response = self.client.post(path=reverse('update_post', kwargs={'slug': self.post_for_getting.slug}), data={'title': 'newTestPost'})
#         self.assertEqual(response.status_code, 302)
#         if Post.objects.get(title='newTestPost'):
#             post = True
#             self.assertTrue(post)
#
#     def test_invalid_update_method(self):
#         response = self.client.post(path=reverse('update_post', kwargs={'slug': self.post_for_getting.slug}), data={'title': ' '})
#         self.assertEqual(response.status_code, 302)
#         if Post.objects.filter(title=' '):
#             post = False
#             self.assertTrue(post)
#
#     def test_valid_create_method(self):
#         response = self.client.post(path=reverse('create_post'),
#                                     data={'title': 'newTestPost1',
#                                           'body': 'testBody',
#                                           'image': image3
#                                           }
#                                     )
#         if Post.objects.get(title='newTestPost1'):
#             post = True
#             self.assertTrue(post)
#             self.assertEqual(response.status_code, 302)
#
#     def test_invalid_create_method(self):
#         response = self.client.post(path=reverse('create_post'),
#                                     data={'title': ' ',
#                                           'body': '123',
#                                           'image': image3
#                                           }
#                                     )
#         if Post.objects.filter(body='123'):
#             post = False
#             self.assertTrue(post)
#             self.assertEqual(response.status_code, 302)
#
#     def test_delete_method(self):
#         response = self.client.post(path=reverse('delete_post', kwargs={'pk': self.post_for_getting.pk}))
#         if Post.objects.filter(title='testPost1'):
#             post = True
#             self.assertFalse(post)
#             self.assertEqual(response.status_code, 302)
#
#
# class TestUserPostsView(TestCase):
#     def setUp(self) -> None:
#         self.user = User.objects.create_user(
#             username='testAdmin',
#             password='testPassword'
#         )
#         self.profile = Profile.objects.create(
#             user=self.user,
#             profile_img=image1,
#             nickname='testNick',
#             about='testAbout'
#         )
#         self.object = Post.objects.create(
#             title='testPost',
#             body='testBody',
#             author=self.user,
#             image=image1,
#         )
#         self.client.login(username='testAdmin', password='testPassword')
#
#     def test_get_method(self):
#         response = self.client.get(path=reverse('user_posts', kwargs={'author': self.profile.nickname}))
#         self.assertEqual(response.status_code, 200)
#         if not Post.objects.filter(author=self.user):
#             post = False
#             self.assertTrue(post)


class TestAllLikesView(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testAdmin',
            password='testPassword'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            profile_img=image1,
            nickname='testNick',
            about='testAbout'
        )
        self.object = Post.objects.create(
            title='testPost',
            body='testBody',
            author=self.user,
            image=image1,
        )
        self.client.login(username='testAdmin', password='testPassword')

    def test_get_method(self):
        response = self.client.get(reverse('likes_list', kwargs={'slug': self.object.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_like(self):
        response = self.client.get(reverse('create_like', kwargs={'slug': self.object.slug}))
