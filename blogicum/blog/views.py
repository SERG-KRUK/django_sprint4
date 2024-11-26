from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .constants import PAGINATE_COUNT
from .services import (annotate_posts_with_comment_count,
                       filter_published_posts, get_paginated_posts)
from .forms import UserForm, PostForm, CommentForm
from .models import Category, Post, User
from .mixins import (
    PostMixin, CommentMixin, AuthorRequiredCommentMixin
)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = annotate_posts_with_comment_count(
        profile.posts)
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
        return get_object_or_404(Category, is_published=True,
                                 slug=self.kwargs['category_slug'])

    def get_queryset(self):
        return annotate_posts_with_comment_count(
            filter_published_posts(self.get_category().posts.all()))

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

        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(filter_published_posts(
            Post.objects.all()), id=self.kwargs['post_id'])


class CommentDeleteView(AuthorRequiredCommentMixin, CommentMixin, DeleteView):
    pass


class CommentUpdateView(AuthorRequiredCommentMixin, CommentMixin, UpdateView):
    pass


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
