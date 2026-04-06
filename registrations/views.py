from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Account, AttachType, Attach, AccountAttach, AccountCondition, AccountNote
from .serializers import (
    AccountSerializer, AccountSimpleSerializer, AttachTypeSerializer,
    AttachSerializer, AccountAttachSerializer, AccountConditionSerializer, AccountNoteSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course', 'course__master', 'course__master__branch', 'student']
    search_fields = ['code', 'student__contact__first_name', 'student__contact__forth_name', 'student__contact__mobile']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccountSimpleSerializer
        return AccountSerializer
    
    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """Get accounts by course"""
        course_id = request.query_params.get('course_id')
        if course_id:
            accounts = Account.objects.filter(course_id=course_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_master(self, request):
        """Get accounts by master"""
        master_id = request.query_params.get('master_id')
        if master_id:
            accounts = Account.objects.filter(course__master_id=master_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'master_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Get accounts by branch"""
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            accounts = Account.objects.filter(course__master__branch_id=branch_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get accounts by student"""
        student_id = request.query_params.get('student_id')
        if student_id:
            accounts = Account.objects.filter(student_id=student_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_mobile(self, request):
        """Search accounts by student mobile"""
        mobile = request.query_params.get('mobile')
        if mobile:
            accounts = Account.objects.filter(student__contact__mobile__icontains=mobile)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'mobile is required'}, status=status.HTTP_400_BAD_REQUEST)


class AttachTypeViewSet(viewsets.ModelViewSet):
    queryset = AttachType.objects.all()
    serializer_class = AttachTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class AttachViewSet(viewsets.ModelViewSet):
    queryset = Attach.objects.all()
    serializer_class = AttachSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['attach_type', 'person']
    search_fields = ['title', 'file_name']


class AccountAttachViewSet(viewsets.ModelViewSet):
    queryset = AccountAttach.objects.all()
    serializer_class = AccountAttachSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account', 'attach']


class AccountConditionViewSet(viewsets.ModelViewSet):
    queryset = AccountCondition.objects.all()
    serializer_class = AccountConditionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account', 'person', 'fulfilled']


class AccountNoteViewSet(viewsets.ModelViewSet):
    queryset = AccountNote.objects.all()
    serializer_class = AccountNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['account', 'person']
