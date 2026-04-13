from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Company, Branch, Bank, MasterCategory
from .serializers import CompanySerializer, BranchSerializer, BankSerializer, MasterCategorySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'email', 'phone1']


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['company']
    search_fields = ['name', 'code', 'email']
    
    # API Endpoint مخصص - مثال
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """إحصائيات الفرع"""
        branch = self.get_object()
        # يمكن إضافة منطق إحصائيات هنا
        data = {
            'branch_id': branch.id,
            'branch_name': branch.name,
            'students_count': 0,  # يمكن ربطها بالنموذج الفعلي
            'courses_count': 0,
            'total_payments': 0
        }
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """قائمة الفروع النشطة"""
        # يمكن إضافة فلترة للفروع النشطة فقط
        branches = self.get_queryset()
        serializer = self.get_serializer(branches, many=True)
        return Response(serializer.data)


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['branch']
    search_fields = ['name', 'account_number', 'iban']


class MasterCategoryViewSet(viewsets.ModelViewSet):
    queryset = MasterCategory.objects.all()
    serializer_class = MasterCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
