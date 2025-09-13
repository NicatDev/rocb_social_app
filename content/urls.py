from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    PostViewSet, ReviewViewSet, LikeViewSet, TagViewSet
)

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'reviews', ReviewViewSet, basename='review') 
router.register(r'likes', LikeViewSet, basename='like') 

posts_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
posts_router.register(r'reviews', ReviewViewSet, basename='post-reviews')
posts_router.register(r'likes', LikeViewSet, basename='post-likes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
]