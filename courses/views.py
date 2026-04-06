from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Master, Course
from .serializers import MasterSerializer, MasterSimpleSerializer, CourseSerializer, CourseSimpleSerializer


class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['branch', 'master_category']
    search_fields = ['name', 'code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MasterSimpleSerializer
        return MasterSerializer
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Get masters by branch"""
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            masters = Master.objects.filter(branch_id=branch_id)
            serializer = MasterSerializer(masters, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['master', 'master__branch']
    search_fields = ['code', 'instructor', 'company_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseSimpleSerializer
        return CourseSerializer
    
    @action(detail=False, methods=['get'])
    def by_master(self, request):
        """Get courses by master"""
        master_id = request.query_params.get('master_id')
        if master_id:
            courses = Course.objects.filter(master_id=master_id)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': 'master_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Get courses by branch"""
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            courses = Course.objects.filter(master__branch_id=branch_id)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)
