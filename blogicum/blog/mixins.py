from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post, Comment
from .forms import PostForm, CommentForm


class AuthorRequiredCommentMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user == self.get_object().author


class PostMixin(AuthorRequiredCommentMixin, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=self.form_class(instance=self.get_object()),
            **kwargs,
        )

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs[self.pk_url_kwarg])

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])
