from django.urls import path
from .views import RegisterView, MyTokenObtainPairView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CourseListView, CourseCreateView, CourseUpdateDeleteView, CourseDetailView
from .views import LessonListView, LessonCreateView, LessonDetailView, LessonUpdateDeleteView
from .views import EnrollView, StudentEnrollmentsView, InstructorCoursesView, CourseEnrolledStudentsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #Courses apis
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/edit/', CourseUpdateDeleteView.as_view(), name='course-update-delete'),
    #Lessons apis
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('courses/<int:course_id>/lessons/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/edit/', LessonUpdateDeleteView.as_view(), name='lesson-update-delete'),
    #Enrollment apis
    path("courses/<int:course_id>/enroll/", EnrollView.as_view(), name="course-enroll"),
    path("students/<int:student_id>/enrollments/", StudentEnrollmentsView.as_view(), name="student-enrollments"),
    # Instructor specific endpoints
    path("instructor/courses/", InstructorCoursesView.as_view(), name="instructor-courses"),
    path("courses/<int:course_id>/students/", CourseEnrolledStudentsView.as_view(), name="course-enrolled-students"),
]
