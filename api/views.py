from rest_framework import generics, permissions, status
from .models import User, Course, Lesson, Enrollment
from .serializers import MyTokenObtainPairSerializer, UserRegistrationSerializer, CourseSerializer, LessonSerializer, EnrollmentSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsInstructorOrAdmin, IsCourseOwnerOrAdmin, IsLessonOwnerOrAdmin
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Count


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # anyone can register


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()   # 🔑 Blacklist the refresh token
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# List all courses (anyone can view)
class CourseListView(generics.ListAPIView):
    # queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Course.objects.all().annotate(
            enrolled_count=Count('enrollments')
        )

    def get_serializer_context(self):
        """Pass request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# Create a course (instructor only)
class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrAdmin]

    def perform_create(self, serializer):
        # Automatically set the instructor to the logged-in user
        serializer.save(instructor=self.request.user)

# Course detail (anyone can view)
class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

# Update/Delete a course
class CourseUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrAdmin, IsCourseOwnerOrAdmin]


# Lessons Views

# 📌 List all lessons in a course
class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(course_id=course_id)


# 📌 Create a lesson in a course (Instructor/Admin only)
class LessonCreateView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrAdmin]

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)

        # ✅ Instructor of the course OR Admin
        if self.request.user.role == 'admin' or course.instructor == self.request.user:
            serializer.save(course=course)
        else:
            raise PermissionDenied("You cannot add lessons to someone else's course.")

# 📌 Get lesson details
class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]

# 📌 Update/Delete lesson (Instructor/Admin only)
class LessonUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrAdmin, IsLessonOwnerOrAdmin]


# Enrollment Views
# 🔹 Student enrolls in a course
class EnrollView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        if request.user.role != "student":
            return Response(
                {"error": "Only students can enroll in courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create enrollment
        enrollment = Enrollment.objects.create(student=request.user, course=course)
        serializer = self.get_serializer(enrollment)
        
        return Response({
            "message": "Successfully enrolled in the course.",
            "enrollment": serializer.data
        }, status=status.HTTP_201_CREATED)


# 🔹 List a student’s enrolled courses
class StudentEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        return Enrollment.objects.filter(student_id=student_id)
    
class InstructorCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrAdmin]

    def get_queryset(self):
        # Only return courses created by the logged-in instructor
        return Course.objects.filter(instructor=self.request.user).annotate(
            enrolled_count=Count('enrollments')
        ).order_by('-created_at')

class CourseEnrolledStudentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsInstructorOrAdmin, IsCourseOwnerOrAdmin]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, pk=course_id)
        
        # Check if the instructor owns this course
        if self.request.user.role != 'admin' and course.instructor != self.request.user:
            raise PermissionDenied("You can only view enrollments for your own courses.")
        
        return Enrollment.objects.filter(course_id=course_id)