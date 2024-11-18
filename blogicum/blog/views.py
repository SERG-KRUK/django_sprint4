from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from .forms import UserForm, PostForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Category, Post, User, Comment
from .constants import POST_QUANTITY
from django.urls import reverse_lazy


def posts_filtered_publications(posts_queryset):
    posts_queryset = posts_queryset.select_related(
        'author', 'location', 'category').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    return posts_queryset


def index(request):
    return render(
        request,
        'blog/index.html',
        {'post_list': posts_filtered_publications(
            Post.objects.all())[:POST_QUANTITY]},
    )


def post_detail(request, id: int):
    post = get_object_or_404(posts_filtered_publications(
        Post.objects.all()), id=id,)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    post_list = posts_filtered_publications(category.posts.all())

    return render(request,
                  'blog/category.html',
                  {'category': category,
                   'post_list': post_list})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
    queryset = Post.objects.all()
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category, slug=category_slug)
        if not self.category.is_published:
            raise Http404("Категория не найдена или снята с публикации.")
        return Post.objects.filter(category=self.category,
                                   is_published=True,
                                   category__is_published=True,
                                   pub_date__lte=timezone.now()
                                   ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.id])

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user.is_superuser or (
            self.request.user == post.author)


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post_id}
        )

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author


class PostDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)

        return context

    def test_func(self):
        post = self.get_object()
        if self.request.user != post.author and (
                not post.is_published):
            raise Http404()

        return self.request.user == post.author or post.is_published

    def handle_no_permission(self):
        return redirect('blog:index')


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.object.post.id})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)
