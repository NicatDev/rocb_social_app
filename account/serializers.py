import datetime
import re
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile, User
from content.serializers import PostSerializer



class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'birth_date', 'profile_picture',
            'country', 'organization', 'position'
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        # User məlumatlarını initial_data-dan al
        user_data = self.initial_data.get('user', {})
        if not user_data:  # initial_data-da user dict yoxdursa
            user_data = {
                'email': self.initial_data.get('email', instance.user.email),
                'first_name': self.initial_data.get('first_name', instance.user.first_name),
                'last_name': self.initial_data.get('last_name', instance.user.last_name),
            }

        # User məlumatlarını update et
        instance.user.email = user_data.get('email', instance.user.email)
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.save()

        # Profile sahələrini update et
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

    # --- VALIDATIONS ---

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        validate_password(value)  # Django password validators
        return value

    def validate_birth_date(self, value):
        if value and value > datetime.date.today():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value

    def validate_phone_number(self, value):
        if value and not re.match(r"^\+?\d{7,15}$", value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_country(self, value):
        if not value.strip():
            raise serializers.ValidationError("Country is required.")
        return value

    # --- CREATE USER & PROFILE ---

    def create(self, validated_data):
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
    
    
class PublicProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'birth_date', 'profile_picture',
            'country', 'organization', 'position', 'count'
        ]
        read_only_fields = fields
