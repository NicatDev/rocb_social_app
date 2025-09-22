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

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    reviews = ReviewSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    review_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)


    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'image', 'file', 'is_active', 
            'created_date', 'tags', 'reviews', 'review_count', 'like_count', 'liked_by_user'
        ]
    

    def get_liked_by_user(self, obj):
        request = self.context.get('request')  # get request from context
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()  # check if current user liked
        return False


class PostApproveSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Post
        fields = [
            'id', 'is_active', 'user', 'content', 'image'
        ]