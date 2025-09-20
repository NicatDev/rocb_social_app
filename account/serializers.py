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

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        user = self.context['request'].user  # use authenticated user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

 
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