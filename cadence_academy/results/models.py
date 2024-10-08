from django.db import models
from django.conf import settings
from accounts.models import CustomUser  

def calculate_grade(total):
    if total >= 90:
        return 'A'
    elif total >= 80:
        return 'B'
    elif total >= 70:
        return 'C'
    elif total >= 60:
        return 'D'
    else:
        return 'F'

def calculate_remark(grade):
    return {
        'A': "Distinction",
        'B': "Upper Credit",
        'C': "Lower Credit",
        'D': "Pass",
        'F': "Fail"
    }.get(grade, "No Remark")

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(CustomUser, related_name='classes', on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(CustomUser, related_name='student_classes')
    subjects = models.ManyToManyField(Subject, related_name='classes')

    def __str__(self):
        return f"{self.name} ({self.teacher.username if self.teacher else 'No teacher assigned'})"

class Result(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    first_test_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    second_test_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def total_score(self):
        return self.first_test_score + self.second_test_score + self.exam_score

    def grade(self):
        return calculate_grade(self.total_score())

    def remark(self):
        return calculate_remark(self.grade())

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}: Total {self.total_score()}, Grade {self.grade()}"

    class Meta:
        unique_together = ('student', 'subject')
