from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comment
from django.urls import reverse
from .forms import PostForm
from django.shortcuts import redirect


class AuthorRequiredCommentMixin(UserPassesTestMixin):

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostMixin(AuthorRequiredCommentMixin, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.object.post.id})
