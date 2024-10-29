from django.urls import path
from .views import SubjectListCreateView, SubjectDetailView, CustomObtainAuthToken, LogoutView, AdminProfileDetailView, UserProfileDetailView, PasswordChangeView, PasswordResetRequestView, PasswordResetConfirmView,  RegisterTeacherView, RegisterStudentView, RegisterAdminView, ClassCreateView, ClassListView, ClassDetailView, ClassUpdateView, ClassDeleteView, TeacherListView, StudentListView, StudentDetailView, StudentUpdateView


urlpatterns = [
    # path('register/', UserRegistrationView.as_view(), name='register'), Take this part to the import just in case I am returning back to it: UserRegistrationView,
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject-detail'),

    path('register/teacher/', RegisterTeacherView.as_view(), name='register-teacher'),
    path('register/student/', RegisterStudentView.as_view(), name='register-student'),
    path('register/admin/', RegisterAdminView.as_view(), name='register-admin'),

    path('login/', CustomObtainAuthToken.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('admin/profile-detail/<int:user_id>/', AdminProfileDetailView.as_view(), name='admin_profile_detail'),
    path('user/profile/<int:user_id>/', UserProfileDetailView.as_view(), name='profile_detail'),
   
    path('classes/create/', ClassCreateView.as_view(), name='class-create'),
    path('classes/', ClassListView.as_view(), name='class-list'),
    path('classes/<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('classes/<int:pk>/update/', ClassUpdateView.as_view(), name='class-update'),
    path('classes/<int:pk>/delete/', ClassDeleteView.as_view(), name='class-delete'),

    path('teachers/', TeacherListView.as_view(), name='teacher-list'),

    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student-update'),
]