from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Contact, Student
from .serializers import ContactSerializer, StudentSerializer, StudentSimpleSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['first_name', 'second_name', 'third_name', 'forth_name', 'mobile', 'identity_number']


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['contact__first_name', 'contact__forth_name', 'contact__mobile', 'contact__identity_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StudentSimpleSerializer
        return StudentSerializer
    
    @action(detail=False, methods=['get'])
    def by_mobile(self, request):
        """Search students by mobile"""
        mobile = request.query_params.get('mobile')
        if mobile:
            students = Student.objects.filter(contact__mobile__icontains=mobile)
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        return Response({'error': 'mobile is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_identity(self, request):
        """Search students by identity number"""
        identity = request.query_params.get('identity')
        if identity:
            students = Student.objects.filter(contact__identity_number__icontains=identity)
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        return Response({'error': 'identity is required'}, status=status.HTTP_400_BAD_REQUEST)
