from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)


class UserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'last_name', 'first_name')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
