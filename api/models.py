from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.

class User(AbstractUser):
    ROLE_CHOISES = (
        ('admin', 'Admin'), 
        ('instructor', 'Instructor'), 
        ('student', 'Student'), 
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # <-- change from default 'user_set'
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set_permissions',  # <-- change from default 'user_set'
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOISES, default='student')

    def __str__(self):
        return f"{self.username}({self.role})"

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_link = models.URLField(blank=True, null=True)
    duration = models.PositiveIntegerField(help_text='Duration in minutes')

    def __str__(self):
        return f"{self.title}({self.course.title})"
    
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")  # prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"