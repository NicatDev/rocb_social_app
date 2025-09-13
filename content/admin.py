from django.contrib import admin
from .models import Post, Tag, Review, Like

@admin.action(description="Seçilmiş postları qəbul et (Accept selected posts)")
def accept_posts(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Seçilmiş postları rədd et (Decline selected posts)")
def decline_posts(modeladmin, request, queryset):
    queryset.update(is_active=False)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_summary', 'created_date', 'is_active')
    search_fields = ('content', 'user__username')
    actions = [accept_posts, decline_posts] 

    def content_summary(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_summary.short_description = 'Content'

admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(Review)
admin.site.register(Like)