from rest_framework import serializers
from .models import User, Course, Lesson, Enrollment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # don't return password in API

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')  # remove password from validated_data
        user = User(**validated_data)  # username, email, role
        user.set_password(password)    # ✅ only the password string

        user.save()
        return user
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token payload
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        
        return token

    def validate(self, attrs):
        # First authenticate the user
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password")
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials!")

        # Call parent validate method
        data = super().validate(attrs)
        
        # Add extra user info to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }
        
        return data
    

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)  # shows username(role)
    enrolled_count = serializers.IntegerField(read_only=True, default=0)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'created_at', 'enrolled_count', 'is_enrolled']
        read_only_fields = ['instructor', 'created_at', 'enrolled_count', 'is_enrolled']

    def get_is_enrolled(self, obj):
        """Check if the current user is enrolled in this course"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            return Enrollment.objects.filter(student=request.user, course=obj).exists()
        return False

class LessonSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_link', 'duration', 'course']
        read_only_fields = ['course']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']
        read_only_fields = ['student', 'course', 'enrolled_at']