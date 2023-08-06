from django.test import TestCase
from .models import Post, PostComment, Profile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
import os
from django.urls import reverse


BASE_DIR = Path(__file__).resolve().parent.parent


class LoginViewTest(TestCase):
    def setUp(self) -> None:
        self.username = 'testUser'
        self.password = 'testPass1'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_login_view_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'incorrectpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignUpViewTest(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

    def test_signup_view_with_valid_credentials(self):
        response = self.client.post(
            reverse('sign_up'),
            {
                'username': 'testUser',
                'password1': 'testPass1',
                'password2': 'testPass1',
                'image': self.image1,
                'nickname': 'testNickname',
                'email': 'testEmail@gmail.com',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signup_view_with_invalid_credentials(self):
        response = self.client.post(
            reverse('sign_up'),
            {
                'username': 'wrongTestUser',
                'password1': 'testPass1',
                'password2': 'testPass2',
                'image': self.image1,
                'nickname': 'wrongTestNickname',
                'email': 'wrongTestEmail@gmail.com',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 0)
        self.assertTrue(response.wsgi_request.user.is_anonymous)


class AllPostsViewTest(TestCase):
    def test_get_method(self):
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)


class DetailedPostViewsCRUDTest(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'), 'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
            username='testAdmin',
            password='testPassword'
        )
        self.post_for_getting = Post.objects.create(
            title='testPost1',
            body='testBody',
            author=self.user,
            image=self.image1,
        )
        self.post_for_posting = Post.objects.create(
            title='testPost2',
            body='testBody',
            author=self.user,
            image=self.image2,
        )

        self.post_for_getting_url = reverse('post', kwargs={'slug': self.post_for_getting.slug})
        self.post_for_posting_url = reverse('post', kwargs={'slug': self.post_for_posting.slug})
        self.client.login(username='testAdmin', password='testPassword')

    def test_valid_get_method(self):
        response = self.client.get(self.post_for_getting_url)
        self.assertTrue(response.status_code, 200)

    def test_invalid_get_method(self):
        response = self.client.get(reverse('post', kwargs={'slug': '122121211'}))
        self.assertTrue(response.status_code, 404)

    # writing a comment for the post
    def test_valid_post_method(self):
        response = self.client.post(path=self.post_for_posting_url, data={'comment': 'Nice Post!'})
        self.assertEqual(response.status_code, 302)

    def test_invalid_post_method(self):
        response = self.client.post(path=self.post_for_posting_url, data={'comment': ''})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PostComment.objects.all())

    # updating the comment for the post
    def test_valid_update_method(self):
        response = self.client.post(
            path=reverse('update_post', kwargs={'slug': self.post_for_getting.slug}),
            data={'title': 'newTestPost'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.get(title='newTestPost'))

    def test_invalid_update_method(self):
        response = self.client.post(
            path=reverse('update_post', kwargs={'slug': self.post_for_getting.slug}),
            data={'title': ' '})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(title=' '))

    # creating a post
    def test_valid_create_method(self):
        response = self.client.post(path=reverse('create_post'),
                                    data={'title': 'newTestPost1',
                                          'body': 'testBody',
                                          'image': self.image1
                                          }
                                    )
        self.assertTrue(Post.objects.get(title='newTestPost1'))
        self.assertEqual(response.status_code, 302)

    def test_invalid_create_method(self):
        response = self.client.post(path=reverse('create_post'),
                                    data={'title': ' ',
                                          'body': '123',
                                          'image': self.image2
                                          }
                                    )
        self.assertFalse(Post.objects.filter(body='123'))
        self.assertEqual(response.status_code, 302)

    # deleting the post
    def test_valid_delete_method(self):
        response = self.client.post(path=reverse('delete_post', kwargs={'pk': self.post_for_getting.pk}))
        self.assertFalse(Post.objects.filter(title='testPost1'))
        self.assertEqual(response.status_code, 302)

    def test_invalid_delete_method(self):
        response = self.client.post(path=reverse('delete_post', kwargs={'pk': 58345263565}))
        self.assertEqual(response.status_code, 404)


class TestUserPostsView(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
            username='testAdmin',
            password='testPassword'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            profile_img=self.image1,
            nickname='testNick',
            about='testAbout'
        )
        self.object = Post.objects.create(
            title='testPost',
            body='testBody',
            author=self.user,
            image=self.image2,
        )
        self.client.login(username='testAdmin', password='testPassword')

    def test_get_method(self):
        response = self.client.get(path=reverse('user_posts', kwargs={'author': self.profile.nickname}))
        self.assertEqual(response.status_code, 200)
        if not Post.objects.filter(author=self.user):
            post = False
            self.assertTrue(post)


class TestAllLikesView(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
            username='testAdmin',
            password='testPassword'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            profile_img=self.image1,
            nickname='testNick',
            about='testAbout'
        )
        self.object = Post.objects.create(
            title='testPost',
            body='testBody',
            author=self.user,
            image=self.image2,
        )
        self.client.login(username='testAdmin', password='testPassword')

    def test_valid_get_method(self):
        response = self.client.get(reverse('likes_list', kwargs={'slug': self.object.slug}))
        self.assertEqual(response.status_code, 200)

    def test_invalid_get_method(self):
        response = self.client.get(reverse('likes_list', kwargs={'slug': '32133213123'}))
        self.assertEqual(response.status_code, 404)

    def test_create_like(self):
        # to like
        response = self.client.get(reverse('create_like', kwargs={'slug': self.object.slug}))
        # to dislike
        response1 = self.client.get(reverse('create_like', kwargs={'slug': self.object.slug}))
        url = reverse('post', kwargs={'slug': self.object.slug})
        self.assertRedirects(response, url)
        self.assertRedirects(response1, url)

        invalid_response = self.client.get(reverse('create_like', kwargs={'slug': '21321312'}))
        self.assertEqual(invalid_response.status_code, 404)


class CommentViewsTest(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
            username='testUser',
            password='testPass1',
        )

        self.client.login(
            username='testUser',
            password='testPass1',
        )

        self.post = Post.objects.create(
            title='testtitle',
            body='testBody',
            image=self.image1,
            author=self.user,
        )

        self.comment = PostComment.objects.create(
            for_post_id=self.post.id,
            who_commented_id=self.user.id,
            comment='testComment'
        )

    def test_update_valid_comment(self):
        response = self.client.post(
            path=reverse(
                'update_comment',
                kwargs={'slug': self.post.slug}),
            data={'comment': 'newComment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PostComment.objects.filter(comment='newComment'))

    def test_update_invalid_comment(self):
        response = self.client.post(
            path=reverse(
                'update_comment',
                kwargs={'slug': self.post.slug}
            ),
            data={'comment': ' '})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PostComment.objects.filter(comment=' '))

    def test_delete_valid_comment(self):
        comment = PostComment.objects.create(
            for_post=self.post,
            who_commented=self.user,
            comment='deletedComment',
        )
        response = self.client.get(reverse('delete_comment', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PostComment.objects.filter(comment='deletedComment'))

    def test_delete_invalid_comment(self):
        response = self.client.get(reverse('delete_comment', kwargs={'pk': 1000321000}))
        self.assertEqual(response.status_code, 404)


class DetailedProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
            username='testUser',
            password='testPass1',
        )
        self.profile = Profile.objects.create(
            user=self.user,
            profile_img=self.image1,
            nickname='testNickname',
            about='testAbout',
        )
        self.client.login(
            username='testUser',
            password='testPass1',
        )

    def test_profile_valid_get_method(self):
        response = self.client.get(reverse('profile'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_profile_invalid_get_method(self):
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/profile/')

    def test_profile_valid_update_method(self):
        response = self.client.post(
            reverse('update_profile'),
            data={'for_nickname': True, 'nickname': 'newNickname',
                  'for_image': True, 'image': self.image2,
                  'for_about': True, 'about': 'newAbout',
                  'for_email': True, 'email': 'newEmail@gmail.com',
                  }
        )
        profile = Profile.objects.get(
            nickname='newNickname',
            about='newAbout',
            user__email='newEmail@gmail.com'
        )
        self.assertTrue(profile)
        self.assertTrue('ocean' in profile.profile_img.name)
        self.assertEqual(response.status_code, 302)

    def test_profile_invalid_update_method(self):
        response = self.client.post(
            reverse('update_profile'),
            data={'for_nickname': True, 'nickname': ' ',
                  'for_image': True, 'image': ' ',
                  'for_about': True, 'about': ' ',
                  'for_email': True, 'email': ' ',
                  }
        )
        profile = Profile.objects.filter(
            nickname=' ',
            about=' ',
            user__email=' '
        )
        self.assertFalse(profile)
        self.assertEqual(response.status_code, 302)


class UserPasswordChangeTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword1'
        )
        self.url = reverse('change_password')
        self.client.login(username='testuser', password='Testpassword1')

    def test_password_change_view_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_password_change(self):
        new_password = 'Newtestpassword1'
        data = {
            'old_password': 'Testpassword1',
            'new_password1': new_password,
            'new_password2': new_password,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))


class FollowersFollowingsLikesFeedbackViewsTest(TestCase):
    def setUp(self) -> None:
        self.image1 = SimpleUploadedFile(
            name='lake.jpg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/lake.jpg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.image2 = SimpleUploadedFile(
            name='ocean.jpeg',
            content=open(os.path.join(BASE_DIR, 'static/test_pics/ocean.jpeg'),
                         'rb').read(),
            content_type='image/jpeg'
        )

        self.user = User.objects.create_user(
                    username='testuser',
                    password='Testpassword1'
                )
        self.profile = Profile.objects.create(
            about='about',
            nickname='nickname',
            profile_img=self.image1,
            user=self.user,
        )
        self.client.login(
            username='testuser',
            password='Testpassword1'
        )

        self.another_user = User.objects.create_user(
            username='anUser',
            password='anPass12'
        )
        self.another_profile = Profile.objects.create(
            user=self.another_user,
            profile_img=self.image2,
            nickname='anotheruser',
            about='about',
        )

    def test_my_followers_view(self):
        response = self.client.get(
            reverse('my_followers')
        )
        self.assertEqual(response.status_code, 200)

    def test_my_followings_view(self):
        response = self.client.get(
            reverse('my_followings')
        )
        self.assertEqual(response.status_code, 200)

    def test_my_likes_view(self):
        response = self.client.get(
            reverse('my_likes')
        )
        self.assertEqual(response.status_code, 200)

    def test_user_followers_view(self):
        response = self.client.get(
            reverse('user_followers', kwargs={'nickname': 'anotheruser'})
        )
        self.assertEqual(response.status_code, 200)

        invalid_response = self.client.get(
            reverse('user_followers', kwargs={'nickname': '313123'})
        )
        self.assertEqual(invalid_response.status_code, 404)

    def test_user_followings_view(self):
        response = self.client.get(
            reverse('user_followings', kwargs={'nickname': 'anotheruser'})
        )
        self.assertEqual(response.status_code, 200)

        invalid_response = self.client.get(
            reverse('user_followings', kwargs={'nickname': '31313312321'})
        )
        self.assertEqual(invalid_response.status_code, 404)

    def test_to_follow_user_view(self):
        # to follow
        response = self.client.get(
            reverse('to_follow_user', kwargs={'pk': self.another_profile.pk})
        )
        follower = self.profile.who_follow.filter(
            who_followed=self.another_profile
        )
        self.assertTrue(follower)

        # to unfollow
        response1 = self.client.get(
            reverse('to_follow_user', kwargs={'pk': self.another_profile.pk})
        )
        follower1 = self.profile.who_follow.filter(
            who_followed=self.another_profile
        )
        self.assertFalse(follower1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response1.status_code, 302)

        invalid_response = self.client.get(
            reverse('to_follow_user', kwargs={'pk': 2340249824982198})
        )

        self.assertEqual(invalid_response.status_code, 404)

    def test_feedback_view_test(self):
        valid_response = self.client.post(
            reverse('feedback'), data={
                'feedback': 'hello'
            }
        )

        invalid_response = self.client.post(
            reverse('feedback'), data={
                'feedback': ' '
            }
        )
        self.assertEqual(valid_response.status_code, 200)
        self.assertEqual(invalid_response.status_code, 302)


class AboutViewTest(TestCase):
    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
