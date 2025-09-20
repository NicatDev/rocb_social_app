from .models import Post, Review, Like, Tag
from .serializers import PostSerializer, ReviewSerializer, LikeSerializer, TagSerializer
from rest_framework import viewsets, permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend 
from .filters import PostFilter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

class BasicPagination(PageNumberPagination):
    page_size = 3

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    pagination_class = BasicPagination
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save(user=self.request.user, is_active=True)
        else:
            serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            review_count=Count('reviews', distinct=True),
            like_count=Count('likes', distinct=True)
        )
        
        is_active_param = self.request.query_params.get('is_active')

        if is_active_param is None:
            return queryset.filter(is_active=True).order_by('-created_date')
        param_lower = is_active_param.lower()
        
        if param_lower == 'true':
            return queryset.filter(is_active=True).order_by('-created_date')
        elif param_lower == 'false':
            return queryset.filter(is_active=False).order_by('-created_date')
        elif param_lower == 'null' or param_lower == 'unknown':
            return queryset.filter(is_active__isnull=True).order_by('-created_date')
        
        own_param = self.request.query_params.get('own')
        if own_param or own_param.lower() == 'true':
            queryset = queryset.filter(user=self.request.user)

        return queryset.filter(is_active=True).order_by('-created_date')

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if 'post_pk' in self.kwargs:
            return self.queryset.filter(post_id=self.kwargs['post_pk'])
        return super().get_queryset()

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if Like.objects.filter(user=self.request.user, post=serializer.validated_data['post']).exists():
            raise serializers.ValidationError({"detail": "You have already liked this post."})
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        if 'post_pk' in self.kwargs:
            return self.queryset.filter(post_id=self.kwargs['post_pk'])
        return super().get_queryset()