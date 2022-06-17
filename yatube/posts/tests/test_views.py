from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

POSTS_GROUP = 11
POSTS_ANOTHER_GROUP = 2
POSTS_SUM = POSTS_GROUP + POSTS_ANOTHER_GROUP
POSTS_INDEX_PAGE2 = POSTS_SUM - settings.POSTS_PER_PAGE
POSTS_GROUP_PAGE2 = POSTS_GROUP - settings.POSTS_PER_PAGE
POSTS_PROFILE_PAGE2 = POSTS_SUM - settings.POSTS_PER_PAGE

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test_slug',
            description='Ещё одна тестовая группа',
        )

        cls.author = User.objects.create_user(username='test_author')

        for i in range(1, POSTS_GROUP + 1):
            Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {i} группы',
                group=cls.group
            )
        for i in range(1, POSTS_ANOTHER_GROUP + 1):
            Post.objects.create(
                author=cls.author,
                text=f'Тестовый пост {i} другой группы',
                group=cls.another_group
            )

        cls.template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostsPagesTests.group.slug,)):
            'posts/group_list.html',
            reverse('posts:profile', args=(PostsPagesTests.author.username,)):
            'posts/profile.html',
            reverse('posts:post_detail', args=(1,)):
            'posts/post_detail.html',
            reverse('posts:post_edit', args=(1,)):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.author)

    def test_pages_use_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for reverse_name, template in (PostsPagesTests
                                       .template_pages_names.items()):
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_page_show_correct_context(self):
        '''Шаблоны страниц с пагинатором имеют правильный контекст.'''
        reverse_qsets = {
            reverse('posts:index'):
            Post.objects.all(),
            reverse(
                'posts:group_list',
                args=(PostsPagesTests.group.slug,)):
            PostsPagesTests.group.posts.select_related(),
            reverse(
                'posts:profile',
                args=(PostsPagesTests.author.username,)):
            PostsPagesTests.author.posts.select_related()
        }

        for reverse_name, qset in reverse_qsets.items():
            response = self.author_client.get(reverse_name)
            for object, post in zip(response.context.get('page_obj'),
                                    qset[:settings.POSTS_PER_PAGE]):
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(object, post)

    def test_first_paginator_page(self):
        '''Проверка: правильное количество постов на 1-й стр. пагинатора.'''
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(PostsPagesTests.group.slug,)),
            reverse('posts:profile', args=(PostsPagesTests.author.username,))
        ]

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
            self.assertEqual(
                len(response.context.get('page_obj')),
                settings.POSTS_PER_PAGE)

    def test_second_paginator_page(self):
        '''Проверка: правильное количество постов на 2-й стр. пагинатора.'''
        reverse_posts = {
            reverse('posts:index'): POSTS_INDEX_PAGE2,
            reverse(
                'posts:group_list',
                args=(PostsPagesTests.group.slug,)):
            POSTS_GROUP_PAGE2,
            reverse(
                'posts:profile',
                args=(PostsPagesTests.author.username,)):
            POSTS_PROFILE_PAGE2
        }

        for reverse_name, number_of_posts in reverse_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj')), number_of_posts)

    def test_post_page_show_correct_context(self):
        '''Шаблон страницы поста имеет правильный контекст.'''
        post = Post.objects.get(pk=1)
        response = self.author_client.get(
            reverse('posts:post_detail', args=(post.pk,)))
        post_from_page = response.context.get('post')

        self.assertEqual(post_from_page, post)

    def test_post_create_page_show_correct_context(self):
        '''Форма создания поста имеет правильные поля.'''
        response = self.author_client.get(reverse('posts:post_create'))

        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_form(self):
        '''Форма создания поста имеет правильные поля.'''
        response = self.author_client.get(reverse('posts:post_create'))

        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        '''Форма редактирования поста имеет правильные поля.'''
        post = Post.objects.get(pk=1)

        response = self.author_client.get(
            reverse('posts:post_edit', args=(post.pk,)))

        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_form_value(self):
        '''Содержимое поста передаётся на страницу редактирования.'''
        post = Post.objects.get(pk=1)

        response = self.author_client.get(
            reverse('posts:post_edit', args=(post.pk,)))
        post_from_page = response.context['form'].instance

        self.assertEqual(post_from_page, post)
        self.assertTrue(response.context['is_edit'])

    def test_new_post_on_its_pages(self):
        '''Новый пост в группе попадает на нужные страницы.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Новый пост группы',
            group=PostsPagesTests.group
        )
        reverse_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', args=(PostsPagesTests.group.slug,)),
            reverse('posts:profile', args=(PostsPagesTests.author.username,))
        ]

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                last_post = response.context.get('page_obj')[0]
                self.assertEqual(last_post, new_post)

        new_post.delete()

    def test_new_post_not_in_another_group(self):
        '''Новый пост в группе не попадает на страницу другой группы.'''
        new_post = Post.objects.create(
            author=PostsPagesTests.author,
            text='Новый пост группы',
            group=PostsPagesTests.group
        )

        response = self.author_client.get(reverse(
            'posts:group_list', args=(PostsPagesTests.another_group.slug,)))

        for post in response.context.get('page_obj'):
            self.assertNotEqual(post.text, new_post.text)

        new_post.delete()
