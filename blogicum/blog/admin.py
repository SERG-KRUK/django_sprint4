from django.contrib import admin

from .models import Category, Location, Post


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    inlines = (
        PostInline,
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )
    search_fields = ('name',)
    list_filter = ('is_published',)
    inlines = (
        PostInline,
    )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category',
        'author',
        'text',
        'pub_date',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('category',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
