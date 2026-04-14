"""
Accounts App - Class-Based Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Team, Person, BranchAccess, Role, EmployeeRole, EmployeePerformance
from .serializers import (
    TeamSerializer, PersonSerializer, PersonCreateSerializer,
    BranchAccessSerializer, RoleSerializer, EmployeeRoleSerializer,
    EmployeePerformanceSerializer
)


# ============================================================
# Authentication Views
# ============================================================

class LoginAPIView(APIView):
    """
    POST /api/auth/login/
    تسجيل الدخول وإرجاع JWT Token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'detail': 'يرجى إدخال البريد الإلكتروني وكلمة المرور'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = Person.objects.get(email=email)
        except Person.DoesNotExist:
            return Response(
                {'detail': 'بيانات الدخول غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.check_password(password):
            return Response(
                {'detail': 'بيانات الدخول غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'الحساب غير نشط'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': PersonSerializer(user).data
        })


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/
    تسجيل الخروج
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'تم تسجيل الخروج بنجاح'})
        except:
            return Response({'detail': 'خطأ في تسجيل الخروج'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# Person (User) Views
# ============================================================

class PersonListCreateAPIView(APIView):
    """
    GET  /api/persons/     → قائمة المستخدمين
    POST /api/persons/     → إنشاء مستخدم جديد
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Person.objects.all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        # Filter by team
        team = request.query_params.get('team')
        if team:
            queryset = queryset.filter(team_id=team)
        
        serializer = PersonSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = PersonCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                PersonSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetailAPIView(APIView):
    """
    GET    /api/persons/<id>/
    PUT    /api/persons/<id>/
    PATCH  /api/persons/<id>/
    DELETE /api/persons/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Person, pk=pk)
    
    def get(self, request, pk):
        person = self.get_object(pk)
        serializer = PersonSerializer(person)
        return Response(serializer.data)
    
    def put(self, request, pk):
        person = self.get_object(pk)
        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        person = self.get_object(pk)
        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        person = self.get_object(pk)
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserAPIView(APIView):
    """
    GET /api/persons/me/
    بيانات المستخدم الحالي
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = PersonSerializer(request.user)
        return Response(serializer.data)


class PersonByBranchAPIView(APIView):
    """
    GET /api/persons/by-branch/?branch_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            persons = Person.objects.filter(branch_id=branch_id)
            serializer = PersonSerializer(persons, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# Team Views
# ============================================================

class TeamListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/teams/
    POST /api/teams/
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]


class TeamDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/teams/<id>/
    PUT /api/teams/<id>/
    DELETE /api/teams/<id>/
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]


# ============================================================
# Role Views
# ============================================================

class RoleListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/roles/
    POST /api/roles/
    """
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class RoleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/roles/<id>/
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


# ============================================================
# EmployeeRole Views
# ============================================================

class EmployeeRoleListCreateAPIView(APIView):
    """
    GET  /api/employee-roles/
    POST /api/employee-roles/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = EmployeeRole.objects.all()
        
        # Filter by person
        person = request.query_params.get('person')
        if person:
            queryset = queryset.filter(person_id=person)
        
        # Filter by branch
        branch = request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        
        serializer = EmployeeRoleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EmployeeRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeRoleDetailAPIView(APIView):
    """
    GET /api/employee-roles/<id>/
    DELETE /api/employee-roles/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(EmployeeRole, pk=pk)
    
    def get(self, request, pk):
        role = self.get_object(pk)
        serializer = EmployeeRoleSerializer(role)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        role = self.get_object(pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# EmployeePerformance Views
# ============================================================

class EmployeePerformanceListCreateAPIView(APIView):
    """
    GET  /api/employee-performances/
    POST /api/employee-performances/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = EmployeePerformance.objects.all()
        
        # Filter by person
        person = request.query_params.get('person')
        if person:
            queryset = queryset.filter(person_id=person)
        
        # Filter by month/year
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(period_month=month, period_year=year)
        
        serializer = EmployeePerformanceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EmployeePerformanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeePerformanceDetailAPIView(APIView):
    """
    GET /api/employee-performances/<id>/
    PUT /api/employee-performances/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(EmployeePerformance, pk=pk)
    
    def get(self, request, pk):
        performance = self.get_object(pk)
        serializer = EmployeePerformanceSerializer(performance)
        return Response(serializer.data)
    
    def put(self, request, pk):
        performance = self.get_object(pk)
        serializer = EmployeePerformanceSerializer(performance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# BranchAccess Views
# ============================================================

class BranchAccessListCreateAPIView(APIView):
    """
    GET  /api/branch-accesses/
    POST /api/branch-accesses/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = BranchAccess.objects.all()
        
        # Filter by person
        person = request.query_params.get('person')
        if person:
            queryset = queryset.filter(person_id=person)
        
        serializer = BranchAccessSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BranchAccessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchAccessDetailAPIView(APIView):
    """
    DELETE /api/branch-accesses/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        access = get_object_or_404(BranchAccess, pk=pk)
        access.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
