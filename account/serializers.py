from rest_framework import serializers
from .models import Profile, User
from content.serializers import PostSerializer

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    posts = PostSerializer(many=True, read_only=True, source='user.posts')

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'birth_date', 'profile_picture',
            'country', 'organization', 'position', 'posts'
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def get_queryset(self):
     return Profile.objects.filter(user=self.request.user)
    
class RegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    # Profile fields
    phone_number = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False)
    profile_picture = serializers.ImageField(required=False)
    country = serializers.CharField()
    organization = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        # User yarat
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=True,      
            is_staff=True,      
            is_superuser=True        
        )

        Profile.objects.create(
            user=user,
            phone_number=validated_data.get('phone_number', ''),
            birth_date=validated_data.get('birth_date', None),
            profile_picture=validated_data.get('profile_picture', None),
            country=validated_data['country'],
            organization=validated_data.get('organization', ''),
            position=validated_data.get('position', ''),
        )

        return user