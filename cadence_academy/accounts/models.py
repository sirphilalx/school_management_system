from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):

   


    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    student_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='students', limit_choices_to={'role': 'student'} )
    

    def __str__(self):
        return self.username
    
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    students = models.ManyToManyField(CustomUser, related_name='subjects', limit_choices_to={'role': 'student'})

    def add_student(self, student):
        if student.role == "student":
            self.students.add(student)
            Score.objects.get_or_create(
                student=student,
                subject=self,
                defaults={'first_test_score': 0.0, 'second_test_score': 0.0, 'exam_score': 0.0}
            )

    def __str__(self):
        return self.name
    
class Score(models.Model):
    student = models.ForeignKey('CustomUser', related_name='score', on_delete=models.CASCADE, limit_choices_to={'role': 'student'} )
    subject = models.ForeignKey(Subject, related_name='score', on_delete=models.CASCADE)
    first_test_score = models.FloatField(default=0.0)
    second_test_score = models.FloatField(default=0.0)
    exam_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} Scores"
    
class Class(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('CustomUser', related_name='classes_taught', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'}  )
    subjects = models.ManyToManyField('Subject', related_name='classes')
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

