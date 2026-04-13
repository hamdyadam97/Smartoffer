"""
Class-Based Views for Core App
API using Django REST Framework CBV instead of ViewSet
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Company, Branch, Bank, MasterCategory
from .serializers import (
    CompanySerializer, BranchSerializer, 
    BankSerializer, MasterCategorySerializer
)


# ============================================================
# Company API (Class-Based Views)
# ============================================================

class CompanyListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/companies/     → List all companies
    POST /api/companies/     → Create new company
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class CompanyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/companies/<id>/  → Retrieve company
    PUT    /api/companies/<id>/  → Update company
    PATCH  /api/companies/<id>/  → Partial update
    DELETE /api/companies/<id>/  → Delete company
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


# ============================================================
# Branch API (Class-Based Views with Custom Actions)
# ============================================================

class BranchListCreateAPIView(APIView):
    """
    GET  /api/branches/     → List branches (with search & filter)
    POST /api/branches/     → Create new branch
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List branches with optional filtering"""
        branches = Branch.objects.all()
        
        # Search by name
        search = request.query_params.get('search')
        if search:
            branches = branches.filter(name__icontains=search)
        
        # Filter by company
        company_id = request.query_params.get('company')
        if company_id:
            branches = branches.filter(company_id=company_id)
        
        serializer = BranchSerializer(branches, many=True)
        return Response({
            'count': branches.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        """Create new branch"""
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchDetailAPIView(APIView):
    """
    GET    /api/branches/<id>/  → Retrieve branch
    PUT    /api/branches/<id>/  → Update branch
    PATCH  /api/branches/<id>/  → Partial update
    DELETE /api/branches/<id>/  → Delete branch
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Branch, pk=pk)
    
    def get(self, request, pk):
        """Get single branch"""
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update branch"""
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        """Partial update branch"""
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete branch"""
        branch = self.get_object(pk)
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BranchStatisticsAPIView(APIView):
    """
    GET /api/branches/<id>/statistics/  → Get branch statistics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        
        # Calculate statistics
        data = {
            'branch_id': branch.id,
            'branch_name': branch.name,
            'total_courses': branch.masters.count(),  # عدد التخصصات
            'total_banks': branch.banks.count(),      # عدد البنوك
            'created_at': branch.created_at,
            'updated_at': branch.updated_at,
        }
        return Response(data)


class BranchActiveListAPIView(APIView):
    """
    GET /api/branches/active/  → List active branches
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # يمكن إضافة منطق للفروع النشطة فقط
        branches = Branch.objects.all().order_by('code')
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)


# ============================================================
# Bank API (Using Mixins for more control)
# ============================================================

class BankListCreateAPIView(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            generics.GenericAPIView):
    """
    Flexible Bank API using Mixins
    """
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['branch']
    search_fields = ['name', 'account_number', 'iban']
    
    def get(self, request, *args, **kwargs):
        """List banks"""
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Create bank"""
        return self.create(request, *args, **kwargs)


class BankDetailAPIView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    """
    Flexible Bank Detail API using Mixins
    """
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Retrieve bank"""
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        """Update bank"""
        return self.update(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """Partial update bank"""
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Delete bank"""
        return self.destroy(request, *args, **kwargs)


# ============================================================
# MasterCategory API (Generic Views - Simplest)
# ============================================================

class MasterCategoryListCreateAPIView(generics.ListCreateAPIView):
    """
    Simple Generic View for MasterCategory
    """
    queryset = MasterCategory.objects.all()
    serializer_class = MasterCategorySerializer
    permission_classes = [IsAuthenticated]


class MasterCategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Simple Generic View for MasterCategory Detail
    """
    queryset = MasterCategory.objects.all()
    serializer_class = MasterCategorySerializer
    permission_classes = [IsAuthenticated]
