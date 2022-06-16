from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import Truncator

from .forms import PostForm
from .models import Group, Post
from .utils import paginate_posts

User = get_user_model()


def index(request):
    """Главная страница."""
    page_obj = paginate_posts(request, Post.objects.select_related())
    context = {'page_obj': page_obj, }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница группы."""
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_posts(
        request,
        group.posts.select_related('author'))
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = paginate_posts(request, author.posts.select_related())
    num_posts = author.posts.count()
    context = {
        'page_obj': page_obj,
        'author': author,
        'num_posts': num_posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    num_posts = post.author.posts.count()
    text_for_title = Truncator(post.text).chars(settings.SYMB_FOR_TITLE)
    is_author = bool(post.author == request.user)
    context = {
        'post': post,
        'num_posts': num_posts,
        'text_for_title': text_for_title,
        'is_author': is_author,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if form.is_valid():
        form_data = form.save(commit=False)
        form_data.author = request.user
        form_data.save()

        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    else:
        form = PostForm(instance=post)

    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id,
    }

    return render(request, 'posts/create_post.html', context)
