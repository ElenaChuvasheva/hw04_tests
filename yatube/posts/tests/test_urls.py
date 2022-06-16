from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.just_user = User.objects.create_user(username='JustUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.just_user)
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.author)

    def test_url_exists_at_desired_location_anonymous(self):
        '''Страницы доступны любому пользователю.'''
        addresses = (
            '/', reverse('posts:group_list', args=(PostsURLTests.group.slug,)),
            reverse('posts:profile', args=(PostsURLTests.author.username,)),
            reverse('posts:post_detail', args=(PostsURLTests.post.pk,)),)
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        '''Запрос к несуществующей странице вернёт ошибку 404.'''
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location(self):
        '''Страница /create/ доступна авторизованному пользователю.'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous(self):
        '''Страницы перенаправляют анонимного пользователя.'''
        addresses = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=(PostsURLTests.post.pk,)))
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница /posts/1/edit/ доступна автору.'''
        response = self.author_client.get(
            reverse('posts:post_edit', args=(PostsURLTests.post.pk,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_non_author_on_login(self):
        """Страница по адресу /posts/1/edit/ перенаправит не-автора на страницу поста.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(PostsURLTests.post.pk,)),
            follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(PostsURLTests.post.pk,))
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            reverse('posts:group_list', args=(PostsURLTests.group.slug,)):
            'posts/group_list.html',
            reverse('posts:profile', args=(PostsURLTests.author.username,)):
            'posts/profile.html',
            reverse('posts:post_detail', args=(PostsURLTests.post.pk,)):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args=(PostsURLTests.post.pk,)):
            'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
