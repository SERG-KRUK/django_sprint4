from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)


from .constants import PAGINATE_COUNT
from .forms import UserForm, PostForm, CommentForm
from .models import Category, Post, User, Comment
from .mixins import (
    PostMixin, CommentMixin, AuthorRequiredCommentMixin
)


def annotate_posts_with_comment_count(posts_queryset):
    return posts_queryset.annotate(comment_count=Count('comments'))


def filter_published_posts(posts_queryset):
    return posts_queryset.select_related(
        'author', 'location', 'category').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')


def get_paginated_posts(request, posts):
    paginator = Paginator(posts, PAGINATE_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date')
    posts = annotate_posts_with_comment_count(posts)
    if request.user != profile:
        posts = filter_published_posts(posts)
    page_obj = get_paginated_posts(request, posts)
    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', args=[username])


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', args=[username])


class PostListView(ListView):
    model = Post
    paginate_by = PAGINATE_COUNT
    template_name = 'blog/index.html'

    def get_queryset(self):
        filtered_posts = filter_published_posts(Post.objects)
        annotated_posts = annotate_posts_with_comment_count(filtered_posts)
        return annotated_posts


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_COUNT

    def get_category(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        if not category.is_published:
            raise Http404("Категория не найдена или снята с публикации.")
        return category

    def get_queryset(self):
        self.category = self.get_category()
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.id])


class PostDeleteView(PostMixin, DeleteView):
    pass


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self):
        """Получаем пост и проверяем авторство пользователя."""
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if self.request.user != post.author and not post.is_published:
            raise Http404("Post not found or not accessible.")
        return post


class CommentDeleteView(AuthorRequiredCommentMixin, CommentMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentUpdateView(AuthorRequiredCommentMixin, CommentMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class CommentCreateView(CommentMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.object.post.id})
