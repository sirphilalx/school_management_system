from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import Profile, CustomUser, Class

# User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'address', 'country', 'date_of_birth', 'user' )
        read_only_fields = ('user',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role'] 

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name', 'teacher')


class TeacherRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='teacher',  # Set user type to teacher
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    


class StudentRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),  
        source='student_profile.class',  
        write_only=True
    )


    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'class_id')

    def create(self, validated_data):
        profile_data = validated_data.pop('student_profile', {})
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='student',  
            class_id='class'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AdminRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            role='admin', 
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)  # Ensure profile data is not required
    role = serializers.CharField(required=False)  # Ensure role is not required

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'profile_picture', 'role', 'profile')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'bio': {'required': False},
            'profile_picture': {'required': False},
            'role': {'required': False},
            'class_id': {'required': False},
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        # Update CustomUser fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Profile fields if profile_data exists
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
