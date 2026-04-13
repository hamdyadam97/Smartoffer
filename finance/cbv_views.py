"""
Finance App - Class-Based Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from .models import (
    Payment, PaymentOut, Deposit, Withdraw,
    BillBuyType, BillBuy, Offer, Call
)
from .serializers import (
    PaymentSerializer, PaymentOutSerializer, DepositSerializer,
    WithdrawSerializer, BillBuyTypeSerializer, BillBuySerializer,
    OfferSerializer, CallSerializer
)


# ============================================================
# Payment (Revenue) Views
# ============================================================

class PaymentListCreateAPIView(APIView):
    """
    GET  /api/payments/     → قائمة سندات القبض
    POST /api/payments/     → إنشاء سند قبض
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Payment.objects.select_related('account').all()
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(code__icontains=search)
        
        # Filter by account
        account = request.query_params.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        
        # Filter by payment type
        payment_type = request.query_params.get('type')
        if payment_type:
            queryset = queryset.filter(type=payment_type)
        
        # Filter by date range
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)
        
        serializer = PaymentSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailAPIView(APIView):
    """
    GET /api/payments/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class PaymentStatisticsAPIView(APIView):
    """
    GET /api/payments/statistics/
    إحصائيات المدفوعات
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total_main = Payment.objects.filter(
            type='ايرادات اساسية'
        ).aggregate(total=Sum('amount_number'))['total'] or 0
        
        total_other = Payment.objects.filter(
            type='ايرادات اخرى'
        ).aggregate(total=Sum('amount_number'))['total'] or 0
        
        return Response({
            'total_main_revenue': total_main,
            'total_other_revenue': total_other,
            'total_revenue': total_main + total_other
        })


# ============================================================
# PaymentOut (Expenses) Views
# ============================================================

class PaymentOutListCreateAPIView(APIView):
    """
    GET  /api/payment-outs/
    POST /api/payment-outs/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = PaymentOut.objects.all()
        
        # Date filter
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)
        
        serializer = PaymentOutSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PaymentOutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# Deposit Views
# ============================================================

class DepositListCreateAPIView(APIView):
    """
    GET  /api/deposits/
    POST /api/deposits/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Deposit.objects.select_related('bank').all()
        
        # Filter by bank
        bank = request.query_params.get('bank')
        if bank:
            queryset = queryset.filter(bank_id=bank)
        
        serializer = DepositSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositDetailAPIView(APIView):
    """
    DELETE /api/deposits/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        deposit = get_object_or_404(Deposit, pk=pk)
        deposit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# Withdraw Views
# ============================================================

class WithdrawListCreateAPIView(APIView):
    """
    GET  /api/withdraws/
    POST /api/withdraws/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Withdraw.objects.select_related('bank').all()
        serializer = WithdrawSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# BillBuy (Purchases) Views
# ============================================================

class BillBuyTypeListCreateAPIView(APIView):
    """
    GET  /api/bill-buy-types/
    POST /api/bill-buy-types/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        types = BillBuyType.objects.all()
        serializer = BillBuyTypeSerializer(types, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BillBuyTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillBuyListCreateAPIView(APIView):
    """
    GET  /api/bill-buys/
    POST /api/bill-buys/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = BillBuy.objects.all()
        
        # Filter by supplier
        supplier = request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier__icontains=supplier)
        
        serializer = BillBuySerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BillBuySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillBuyDetailAPIView(APIView):
    """
    GET /api/bill-buys/<id>/
    DELETE /api/bill-buys/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        bill = get_object_or_404(BillBuy, pk=pk)
        serializer = BillBuySerializer(bill)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        bill = get_object_or_404(BillBuy, pk=pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# Offer Views
# ============================================================

class OfferListCreateAPIView(APIView):
    """
    GET  /api/offers/
    POST /api/offers/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Offer.objects.select_related('master').all()
        
        # Search by customer
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(customer_name__icontains=search)
        
        # Filter by master
        master = request.query_params.get('master')
        if master:
            queryset = queryset.filter(master_id=master)
        
        # Filter by registered status
        registered = request.query_params.get('registered')
        if registered is not None:
            queryset = queryset.filter(registered=registered.lower() == 'true')
        
        serializer = OfferSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def post(self, request):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(last_person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailAPIView(APIView):
    """
    GET /api/offers/<id>/
    PUT /api/offers/<id>/
    DELETE /api/offers/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        return get_object_or_404(Offer, pk=pk)
    
    def get(self, request, pk):
        offer = self.get_object(pk)
        serializer = OfferSerializer(offer)
        return Response(serializer.data)
    
    def put(self, request, pk):
        offer = self.get_object(pk)
        serializer = OfferSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        offer = self.get_object(pk)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferConvertAPIView(APIView):
    """
    POST /api/offers/<id>/convert/
    تحويل عرض السعر إلى تسجيل
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        offer.registered = True
        offer.save()
        return Response({'detail': 'تم تحويل العرض إلى تسجيل'})


# ============================================================
# Call Views
# ============================================================

class CallListCreateAPIView(APIView):
    """
    GET  /api/calls/
    POST /api/calls/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Call.objects.select_related('offer', 'person').all()
        
        # Filter by offer
        offer = request.query_params.get('offer')
        if offer:
            queryset = queryset.filter(offer_id=offer)
        
        # Filter by person
        person = request.query_params.get('person')
        if person:
            queryset = queryset.filter(person_id=person)
        
        serializer = CallSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(person=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CallDetailAPIView(APIView):
    """
    DELETE /api/calls/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        call = get_object_or_404(Call, pk=pk)
        call.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
