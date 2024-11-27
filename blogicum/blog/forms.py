from django import forms
from django.utils import timezone

from .models import Post, Comment, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'text': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        if 'pub_date' in self.fields:
            self.fields['pub_date'].initial = timezone.now()


class UserForm(forms.ModelForm):
    class Meta:
        model = User  # Используем вашу собственную модель пользователя
        fields = ('username', 'email', 'last_name', 'first_name')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
