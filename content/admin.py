from django.contrib import admin
from .models import Post, Tag, Review, Like


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    fields = ('user', 'content', 'created_date')
    readonly_fields = ('created_date',)


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    fields = ('user', 'created_date')
    readonly_fields = ('created_date',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_summary', 'is_active', 'created_date')
    list_filter = ('is_active', 'created_date', 'tags')
    search_fields = ('content', 'user__username', 'tags__name')
    date_hierarchy = 'created_date'
    filter_horizontal = ('tags',)
    inlines = [ReviewInline, LikeInline]

    def content_summary(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_summary.short_description = 'Content'


# Tags separately
admin.site.register(Tag)