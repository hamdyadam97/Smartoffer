"""
Students App - Class-Based Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Contact, Student
from .serializers import ContactSerializer, StudentSerializer


# ============================================================
# Contact Views
# ============================================================

class ContactListCreateAPIView(APIView):
    """
    GET  /api/contacts/     → قائمة جهات الاتصال
    POST /api/contacts/     → إنشاء جهة اتصال
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Contact.objects.all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                mobile__icontains=search
            ) | queryset.filter(
                identity_number__icontains=search
            )
        
        serializer = ContactSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetailAPIView(APIView):
    """
    GET    /api/contacts/<id>/
    PUT    /api/contacts/<id>/
    PATCH  /api/contacts/<id>/
    DELETE /api/contacts/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Contact, pk=pk)
    
    def get(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact)
        return Response(serializer.data)
    
    def put(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        contact = self.get_object(pk)
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        contact = self.get_object(pk)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# Student Views
# ============================================================

class StudentListCreateAPIView(APIView):
    """
    GET  /api/students/     → قائمة الطلاب
    POST /api/students/     → إنشاء طالب
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Student.objects.select_related('contact').all()
        
        # Search by contact name
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                contact__first_name__icontains=search
            ) | queryset.filter(
                contact__forth_name__icontains=search
            ) | queryset.filter(
                contact__mobile__icontains=search
            )
        
        # Filter by level
        level = request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by preferred contact
        preferred = request.query_params.get('preferred_contact')
        if preferred:
            queryset = queryset.filter(preferred_contact=preferred)
        
        serializer = StudentSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        # يمكن إنشاء طالب مع جهة اتصال جديدة أو موجودة
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailAPIView(APIView):
    """
    GET    /api/students/<id>/
    PUT    /api/students/<id>/
    PATCH  /api/students/<id>/
    DELETE /api/students/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Student, pk=pk)
    
    def get(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    
    def put(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        student = self.get_object(pk)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentCoursesAPIView(APIView):
    """
    GET /api/students/<id>/courses/
    دورات الطالب المسجل فيها
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        accounts = student.accounts.select_related('course').all()
        
        courses_data = []
        for account in accounts:
            courses_data.append({
                'account_id': account.id,
                'course': account.course.name if account.course else None,
                'registration_date': account.register_date,
                'payment_status': account.get_paid_price(),
                'remaining': account.get_remain_price()
            })
        
        return Response(courses_data)


class StudentByMobileAPIView(APIView):
    """
    GET /api/students/by-mobile/?mobile=<value>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobile = request.query_params.get('mobile')
        if mobile:
            students = Student.objects.filter(contact__mobile__icontains=mobile)
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        return Response({'error': 'mobile is required'}, status=status.HTTP_400_BAD_REQUEST)


class StudentByIdentityAPIView(APIView):
    """
    GET /api/students/by-identity/?identity=<value>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        identity = request.query_params.get('identity')
        if identity:
            students = Student.objects.filter(contact__identity_number__icontains=identity)
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        return Response({'error': 'identity is required'}, status=status.HTTP_400_BAD_REQUEST)
