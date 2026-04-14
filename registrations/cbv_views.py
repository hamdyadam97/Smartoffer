"""
Registrations App - Class-Based Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Account, AttachType, Attach, AccountAttach, AccountCondition, AccountNote
from .serializers import (
    AccountSerializer, AttachTypeSerializer, AttachSerializer,
    AccountAttachSerializer, AccountConditionSerializer, AccountNoteSerializer
)


# ============================================================
# Account (Registration) Views
# ============================================================

class AccountListCreateAPIView(APIView):
    """
    GET  /api/accounts/     → قائمة التسجيلات
    POST /api/accounts/     → تسجيل طالب في دورة
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Account.objects.select_related(
            'student', 'student__contact', 'course', 'course__master'
        ).all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                student__contact__first_name__icontains=search
            ) | queryset.filter(
                student__contact__forth_name__icontains=search
            )
        
        # Filter by course
        course = request.query_params.get('course')
        if course:
            queryset = queryset.filter(course_id=course)
        
        # Filter by student
        student = request.query_params.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        
        # Filter by payment type
        payment_type = request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(course_payment_type=payment_type)
        
        serializer = AccountSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        with transaction.atomic():
            serializer = AccountSerializer(data=request.data)
            if serializer.is_valid():
                account = serializer.save()
                return Response(
                    AccountSerializer(account).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailAPIView(APIView):
    """
    GET    /api/accounts/<id>/
    PUT    /api/accounts/<id>/
    PATCH  /api/accounts/<id>/
    DELETE /api/accounts/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Account, pk=pk)
    
    def get(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account)
        return Response(serializer.data)
    
    def put(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        account = self.get_object(pk)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountPaymentsAPIView(APIView):
    """
    GET /api/accounts/<id>/payments/
    المدفوعات الخاصة بالتسجيل
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        payments = account.payments.all()
        
        data = []
        for payment in payments:
            data.append({
                'id': payment.id,
                'code': payment.code,
                'date': payment.date,
                'amount': payment.amount_number,
                'type': payment.type,
                'payment_method': payment.payment_method
            })
        
        return Response({
            'account_key': account.get_key(),
            'required_price': account.get_required_price(),
            'paid_price': account.get_paid_price(),
            'remaining': account.get_remain_price(),
            'payments': data
        })


class AccountSummaryAPIView(APIView):
    """
    GET /api/accounts/summary/
    ملخص التسجيلات
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total_accounts = Account.objects.count()
        total_paid = sum(
            acc.get_paid_price() for acc in Account.objects.all()
        )
        total_remaining = sum(
            acc.get_remain_price() for acc in Account.objects.all()
        )
        
        return Response({
            'total_accounts': total_accounts,
            'total_paid': round(total_paid, 2),
            'total_remaining': round(total_remaining, 2),
            'total_expected': round(total_paid + total_remaining, 2)
        })


class AccountByCourseAPIView(APIView):
    """
    GET /api/accounts/by-course/?course_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        if course_id:
            accounts = Account.objects.filter(course_id=course_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class AccountByMasterAPIView(APIView):
    """
    GET /api/accounts/by-master/?master_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        master_id = request.query_params.get('master_id')
        if master_id:
            accounts = Account.objects.filter(course__master_id=master_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'master_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class AccountByBranchAPIView(APIView):
    """
    GET /api/accounts/by-branch/?branch_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            accounts = Account.objects.filter(course__master__branch_id=branch_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class AccountByStudentAPIView(APIView):
    """
    GET /api/accounts/by-student/?student_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        if student_id:
            accounts = Account.objects.filter(student_id=student_id)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class AccountByMobileAPIView(APIView):
    """
    GET /api/accounts/by-mobile/?mobile=<value>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobile = request.query_params.get('mobile')
        if mobile:
            accounts = Account.objects.filter(student__contact__mobile__icontains=mobile)
            serializer = AccountSerializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'mobile is required'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# Attach Views
# ============================================================

class AttachTypeListCreateAPIView(APIView):
    """
    GET  /api/attach-types/
    POST /api/attach-types/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        types = AttachType.objects.all()
        serializer = AttachTypeSerializer(types, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AttachTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttachListCreateAPIView(APIView):
    """
    GET  /api/attaches/
    POST /api/attaches/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Attach.objects.all()
        
        # Filter by type
        attach_type = request.query_params.get('type')
        if attach_type:
            queryset = queryset.filter(attach_type_id=attach_type)
        
        serializer = AttachSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AttachSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttachDetailAPIView(APIView):
    """
    GET /api/attaches/<id>/
    DELETE /api/attaches/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        attach = get_object_or_404(Attach, pk=pk)
        serializer = AttachSerializer(attach)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        attach = get_object_or_404(Attach, pk=pk)
        attach.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# AccountAttach Views
# ============================================================

class AccountAttachListCreateAPIView(APIView):
    """
    GET  /api/account-attaches/
    POST /api/account-attaches/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = AccountAttach.objects.all()
        
        # Filter by account
        account = request.query_params.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        
        serializer = AccountAttachSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AccountAttachSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# AccountCondition Views
# ============================================================

class AccountConditionListCreateAPIView(APIView):
    """
    GET  /api/account-conditions/
    POST /api/account-conditions/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = AccountCondition.objects.all()
        
        # Filter by account
        account = request.query_params.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        
        # Filter by fulfilled status
        fulfilled = request.query_params.get('fulfilled')
        if fulfilled is not None:
            queryset = queryset.filter(fulfilled=fulfilled.lower() == 'true')
        
        serializer = AccountConditionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AccountConditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountConditionDetailAPIView(APIView):
    """
    GET /api/account-conditions/<id>/
    PUT /api/account-conditions/<id>/
    DELETE /api/account-conditions/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(AccountCondition, pk=pk)
    
    def get(self, request, pk):
        condition = self.get_object(pk)
        serializer = AccountConditionSerializer(condition)
        return Response(serializer.data)
    
    def put(self, request, pk):
        condition = self.get_object(pk)
        serializer = AccountConditionSerializer(condition, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# AccountNote Views
# ============================================================

class AccountNoteListCreateAPIView(APIView):
    """
    GET  /api/account-notes/
    POST /api/account-notes/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = AccountNote.objects.all()
        
        # Filter by account
        account = request.query_params.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        
        serializer = AccountNoteSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AccountNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountNoteDetailAPIView(APIView):
    """
    DELETE /api/account-notes/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        note = get_object_or_404(AccountNote, pk=pk)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
