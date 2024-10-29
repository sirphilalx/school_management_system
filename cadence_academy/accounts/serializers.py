from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import Profile, CustomUser, Class, Subject, Score


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

    student_class = serializers.StringRelatedField()
    subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'student_class', 'subjects']

    def get_subjects(self, obj):
        """Gets the subjects associated with the student's class."""
        if obj.role == 'student' and obj.student_class:
            return [subject.name for subject in obj.student_class.subjects.all()]
        return [] 
    
class ClassSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='teacher'), required=False)
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True, required=False)
    students = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='student'), many=True, required=False)
   
    class Meta:
        model = Class
        fields = ['id', 'name', 'teacher', 'students', 'subjects']

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['first_test_score', 'second_test_score', 'exam_score']

class SubjectScoreSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['name', 'code', 'score']

    
    def get_score(self, obj):
        request = self.context.get('request')
        
        if request.user.role != 'student':
            
            student_id = self.context.get('student_id')
        else:
            student_id = request.user.id

        scores = Score.objects.filter(student_id=student_id, subject=obj).first()
        return ScoreSerializer(scores).data if scores else None


class StudentListSerializer(serializers.ModelSerializer):
    student_class = serializers.StringRelatedField()  

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role','student_class']


class StudentDetailSerializer(serializers.ModelSerializer):
    student_class = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all(), required=False)
    subjects = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'student_class', 'subjects']
        extra_kwargs = {
            'username': {'required': False},
            'student_class': {'required': False},
            'subject': {'required': False}
        }

    def get_subjects(self, obj):
        student_class = obj.student_class
        if student_class:
            subjects = student_class.subjects.all()
            subject_data = []
            for subject in subjects:
                score = Score.objects.filter(student=obj, subject=subject).first()
                score_data = ScoreSerializer(score).data if score else None
                data = {
                    "id": subject.id,
                    "name": subject.name,
                    "code": subject.code,
                    "score": score_data
                }
                subject_data.append(data)
                print(data)  # Debug: check the constructed data
            return subject_data
        return []

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.student_class = validated_data.get('student_class', instance.student_class)
        instance.save()
        return instance
    

class StudentClassUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'classes']
        extra_kwargs = {'classes': {'required': True}}

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
    
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']

    def get_scores(self, obj):
        student = self.context.get('student')
        score = Score.objects.filter(student=student, subject=obj).first()
        return ScoreSerializer(score).data if score else None

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
    profile = ProfileSerializer(required=False)   
    role = serializers.CharField(required=False)  

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
