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
