"""
Courses App - Class-Based Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Master, Course
from .serializers import MasterSerializer, CourseSerializer


# ============================================================
# Master (Specialization) Views
# ============================================================

class MasterListCreateAPIView(APIView):
    """
    GET  /api/masters/     → قائمة التخصصات
    POST /api/masters/     → إنشاء تخصص
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Master.objects.select_related('branch', 'master_category').all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filter by branch
        branch = request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(master_category_id=category)
        
        serializer = MasterSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = MasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MasterDetailAPIView(APIView):
    """
    GET    /api/masters/<id>/
    PUT    /api/masters/<id>/
    PATCH  /api/masters/<id>/
    DELETE /api/masters/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Master, pk=pk)
    
    def get(self, request, pk):
        master = self.get_object(pk)
        serializer = MasterSerializer(master)
        return Response(serializer.data)
    
    def put(self, request, pk):
        master = self.get_object(pk)
        serializer = MasterSerializer(master, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        master = self.get_object(pk)
        serializer = MasterSerializer(master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        master = self.get_object(pk)
        master.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MasterCoursesAPIView(APIView):
    """
    GET /api/masters/<id>/courses/
    الدورات التابعة للتخصص
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        master = get_object_or_404(Master, pk=pk)
        courses = master.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


# ============================================================
# Course Views
# ============================================================

class CourseListCreateAPIView(APIView):
    """
    GET  /api/courses/     → قائمة الدورات
    POST /api/courses/     → إنشاء دورة
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Course.objects.select_related('master').all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                instructor__icontains=search
            ) | queryset.filter(
                company_name__icontains=search
            )
        
        # Filter by master
        master = request.query_params.get('master')
        if master:
            queryset = queryset.filter(master_id=master)
        
        # Filter by target level
        level = request.query_params.get('target_level')
        if level:
            queryset = queryset.filter(target_level=level)
        
        # Filter by date range
        start_after = request.query_params.get('start_after')
        if start_after:
            queryset = queryset.filter(start_date__gte=start_after)
        
        serializer = CourseSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailAPIView(APIView):
    """
    GET    /api/courses/<id>/
    PUT    /api/courses/<id>/
    PATCH  /api/courses/<id>/
    DELETE /api/courses/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Course, pk=pk)
    
    def get(self, request, pk):
        course = self.get_object(pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
    def put(self, request, pk):
        course = self.get_object(pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        course = self.get_object(pk)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        course = self.get_object(pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseStudentsAPIView(APIView):
    """
    GET /api/courses/<id>/students/
    الطلاب المسجلين في الدورة
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        accounts = course.accounts.select_related('student', 'student__contact').all()
        
        students_data = []
        for account in accounts:
            student = account.student
            students_data.append({
                'account_id': account.id,
                'student_id': student.id,
                'student_name': student.get_full_name(),
                'mobile': student.get_mobile(),
                'registration_date': account.register_date,
                'payment_type': account.course_payment_type,
                'paid': account.get_paid_price(),
                'remaining': account.get_remain_price()
            })
        
        return Response(students_data)


class CourseStatisticsAPIView(APIView):
    """
    GET /api/courses/<id>/statistics/
    إحصائيات الدورة
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        accounts = course.accounts.all()
        
        total_students = accounts.count()
        total_paid = sum(acc.get_paid_price() for acc in accounts)
        total_remaining = sum(acc.get_remain_price() for acc in accounts)
        
        data = {
            'course_id': course.id,
            'course_name': course.master.name if course.master else None,
            'max_students': course.max_student_count,
            'current_students': total_students,
            'available_seats': course.max_student_count - total_students,
            'total_paid': total_paid,
            'total_remaining': total_remaining,
            'fill_percentage': round((total_students / course.max_student_count) * 100, 2) if course.max_student_count > 0 else 0
        }
        return Response(data)
