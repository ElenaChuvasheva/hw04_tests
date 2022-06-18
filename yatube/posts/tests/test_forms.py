from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test_slug',
            description='Тестовое описание другой группы',
        )
        cls.author = User.objects.create_user(username='JustUser')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост группы',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)

    def test_create_post(self):
        '''Валидная форма создаёт запись в Post.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': PostFormTests.group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=(PostFormTests.author.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст нового поста',
                author=PostFormTests.author,
                group=PostFormTests.group
            ).exists()
        )

    def test_edit_post(self):
        '''Валидная форма изменяет запись в Post.'''
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Обновлённый текст поста',
            'group': PostFormTests.another_group.pk
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(PostFormTests.post.pk,)),
            data=form_data,
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(PostFormTests.post.pk,)))
        self.assertTrue(
            Post.objects.filter(
                text='Обновлённый текст поста',
                author=PostFormTests.author,
                group=PostFormTests.another_group
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)
