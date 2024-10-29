from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer,StudentListSerializer, SubjectSerializer, ClassSerializer, UserProfileSerializer, PasswordChangeSerializer, ProfileSerializer, TeacherRegistrationSerializer, StudentRegistrationSerializer, AdminRegistrationSerializer, ClassSerializer, CustomUserSerializer, StudentClassUpdateSerializer, StudentDetailSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import Profile, CustomUser, Class, Subject
from .permissions import IsAdminUser, IsTeacherUser, IsStudentUser, IsAdminOrTeacherUser
from rest_framework.decorators import api_view

User = CustomUser

# Registration View
# class UserRegistrationView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserRegistrationSerializer
#     permission_classes = [permissions.AllowAny]


# class ClassCreateUpdateView(generics.CreateAPIView, generics.UpdateAPIView):
#     queryset = Class.objects.all()
#     serializer_class = ClassSerializer
#     permission_classes = [IsAdminUser]

class ClassCreateView(generics.CreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminUser] 

    def perform_create(self, serializer):
        serializer.save()

class ClassListView(generics.ListAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]  

class ClassDetailView(generics.RetrieveAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated] 

class ClassUpdateView(generics.UpdateAPIView):
    # queryset = Class.objects.all()
    # serializer_class = ClassSerializer
    # permission_classes = [IsAdminUser]  

    # def perform_update(self, serializer):
    #     serializer.save()

    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ClassDeleteView(generics.DestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminUser] 

class SubjectListCreateView(APIView):
    permission_classes = [IsAdminUser]


    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailView(APIView):
    def get_object(self, pk):
        try:
            return Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        subject = self.get_object(pk)
        serializer = SubjectSerializer(subject)
        return Response(serializer.data)

    def put(self, request, pk):
        subject = self.get_object(pk)
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subject = self.get_object(pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.filter(role='student')  # Ensure we only deal with students
    serializer_class = StudentDetailSerializer
    lookup_field = 'id'  # Assuming you lookup by student ID

    def get(self, request, *args, **kwargs):
        """Retrieve the specified student's details."""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Update the specified student's details."""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Partially update the specified student's details."""
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Override update to include custom logic if needed."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to forcibly
            # invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class RegisterTeacherView(generics.CreateAPIView):
    serializer_class = TeacherRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class TeacherListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]  

    def get_queryset(self):
        return CustomUser.objects.filter(role='teacher')

class StudentListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(role='student')
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.filter(role='student')

class StudentDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.filter(role='student')
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

class StudentUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.filter(role='student')
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAdminOrTeacherUser]

class RegisterStudentView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class RegisterAdminView(generics.CreateAPIView):
    serializer_class = AdminRegistrationSerializer
    permission_classes = [permissions.AllowAny]

# Login View
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'role': user.role
        })

# Logout View
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=204)

# Admin Profile View (Admin can view and update any profile)
class AdminProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return Profile.objects.get(user__id=user_id)

# User Profile View (Any authenticated user can view and update their profile)
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'



    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Profile, user__id=user_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Password Change View
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")

            if not request.user.check_password(old_password):
                return Response({"old_password": "Wrong password."}, status=400)

            request.user.set_password(new_password)
            request.user.save()
            return Response({"detail": "Password has been changed."})
        return Response(serializer.errors, status=400)
    


@api_view(['PATCH'])
def update_profile(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Request View
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # In real application, send this reset information via email
            reset_link = f"reset/{uid}/{token}/"
            return Response({"reset_link": reset_link})
        return Response({"email": "No user found with this email address."}, status=400)

# Password Reset Confirm View
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get("new_password")
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."})
        return Response({"detail": "Invalid reset link."}, status=400)

class TeacherView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser]

    def get_object(self):
        return self.request.user.profile

# Student View (Students can view their profile)
class StudentView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentUser]

    def get_object(self):
        return self.request.user.profile