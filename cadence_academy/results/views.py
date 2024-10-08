from rest_framework import viewsets
from .models import Subject, Class, Result
from .serializers import SubjectSerializer, ClassSerializer, ResultSerializer
from rest_framework.permissions import IsAuthenticated

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Additional logic here if needed
        serializer.save()
