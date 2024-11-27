from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import PAGINATE_COUNT


def annotate_posts_with_comment_count(posts, annotate=True):
    return posts.select_related(
        'author', 'location', 'category').annotate(
            comment_count=Count('comments')).order_by('-pub_date')


def filter_published_posts(posts_queryset):
    return posts_queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def get_paginated_posts(request, posts):
    paginator = Paginator(posts, PAGINATE_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
