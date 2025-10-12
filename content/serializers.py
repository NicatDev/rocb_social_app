from rest_framework import serializers
from .models import Post, Review, Like, Tag
from django.contrib.auth.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'post', 'content', 'created_date']

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_date']

class SimpleUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source='profile.profile_picture', read_only=True)

    class Meta:
        model = User
        # Frontend-də ehtiyacımız olan sahələri müəyyən edirik
        fields = ['id', 'first_name', 'last_name', 'profile_picture']
        
class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    reviews = ReviewSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    liked_by_user = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)


    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'image', 'file', 'is_active', 
            'created_date', 'tags', 'reviews', 'review_count', 'like_count', 'liked_by_user'
        ]
    

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = obj.likes.filter(user=request.user).first()  # get Like object if exists
            if like:
                return like.id  # return id for unlike
        return None


class PostApproveSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Post
        fields = [
            'id', 'is_active', 'user', 'content', 'image'
        ]

class TopPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile.profile_picture', read_only=True)
    
    # Like və review count
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    review_count = serializers.IntegerField(source='reviews.count', read_only=True)

    # Orijinal PostSerializer-dən olan sahələr
    reviews = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id',
            'content',
            'username',
            'user',
            'first_name',
            'last_name',
            'profile_picture',
            'image',
            'file',
            'is_active',
            'created_date',
            'tags',
            'reviews',
            'review_count',
            'like_count',
            'liked_by_user',
        ]

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = obj.likes.filter(user=request.user).first()
            if like:
                return like.id
        return None

    def get_reviews(self, obj):
        from .serializers import ReviewSerializer  # ReviewSerializer import et
        return ReviewSerializer(obj.reviews.all(), many=True, context=self.context).data

    def get_tags(self, obj):
        from .serializers import TagSerializer  # TagSerializer import et
        return TagSerializer(obj.tags.all(), many=True, context=self.context).data