from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, ClassViewSet, ResultViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'results', ResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]