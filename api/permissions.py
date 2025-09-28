from rest_framework import permissions
from .models import Enrollment

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'instructor' or 'admin'.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['instructor', 'admin']
        )


class IsCourseOwnerOrAdmin(permissions.BasePermission):
    """
    Only the instructor who created the course or an admin can update/delete it.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'admin' or
            obj.instructor == request.user
        )


class IsLessonOwnerOrAdmin(permissions.BasePermission):
    """
    Allow only the course instructor (who owns the lesson's course)
    or admin to modify/delete lessons.
    """
    def has_object_permission(self, request, view, obj):
        # obj is a Lesson instance
        return (
            request.user.role == "admin" or
            obj.course.instructor == request.user
        )
    
class IsEnrolledOrInstructorOrAdmin(permissions.BasePermission):
    """
    Students must be enrolled in the course to view lessons.
    Instructor & Admin always allowed.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ['admin', 'instructor'] and (
            user == obj.course.instructor or user.role == 'admin'
        ):
            return True
        return Enrollment.objects.filter(student=user, course=obj.course).exists()