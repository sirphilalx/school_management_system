from rest_framework import serializers
from .models import Subject, Class, Result
from accounts.models import CustomUser

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Adjust this if your student model is different
        fields = ['id', 'username', 'email']  # Add other fields as needed

class ClassSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)
    subjects = SubjectSerializer(many=True, read_only=True)
    teacher = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'teacher', 'students', 'subjects']

    def create(self, validated_data):
        return Class.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Allow updates to all fields, including students and subjects
        instance.name = validated_data.get('name', instance.name)

        # Handling teacher update if it is not read-only
        teacher_data = validated_data.get('teacher', None)
        if teacher_data:
            instance.teacher = CustomUser.objects.get(username=teacher_data.get('username'))

        instance.save()
        return instance

class ResultSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    subject = SubjectSerializer()
    total_score = serializers.FloatField(read_only=True)
    grade = serializers.CharField(read_only=True)
    remark = serializers.CharField(read_only=True)

    class Meta:
        model = Result
        fields = [
            'id', 'student', 'subject', 'first_test_score',
            'second_test_score', 'exam_score', 'total_score',
            'grade', 'remark', 'date_recorded'
        ]
