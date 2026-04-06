from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Payment, PaymentOut, Deposit, Withdraw, BillBuyType, BillBuy, Offer, Call
from .serializers import (
    PaymentSerializer, PaymentOutSerializer, DepositSerializer,
    WithdrawSerializer, BillBuyTypeSerializer, BillBuySerializer,
    OfferSerializer, CallSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['account', 'account__course', 'account__course__master__branch', 'type', 'payment_method']
    search_fields = ['code', 'account__student__contact__first_name', 'account__student__contact__forth_name']
    
    @action(detail=False, methods=['get'])
    def by_account(self, request):
        """Get payments by account"""
        account_id = request.query_params.get('account_id')
        if account_id:
            payments = Payment.objects.filter(account_id=account_id)
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data)
        return Response({'error': 'account_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Get payments by branch"""
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            payments = Payment.objects.filter(account__course__master__branch_id=branch_id)
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentOutViewSet(viewsets.ModelViewSet):
    queryset = PaymentOut.objects.all()
    serializer_class = PaymentOutSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_method']
    search_fields = ['code', 'receiver_name']


class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bank']


class WithdrawViewSet(viewsets.ModelViewSet):
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bank']


class BillBuyTypeViewSet(viewsets.ModelViewSet):
    queryset = BillBuyType.objects.all()
    serializer_class = BillBuyTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class BillBuyViewSet(viewsets.ModelViewSet):
    queryset = BillBuy.objects.all()
    serializer_class = BillBuySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['bill_buy_type']
    search_fields = ['code', 'supplier']


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['master', 'master__branch', 'registered', 'master_payment_type']
    search_fields = ['code', 'customer_name', 'customer_mobile', 'customer_identity_number']
    
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        """Get offers by branch"""
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            offers = Offer.objects.filter(master__branch_id=branch_id)
            serializer = OfferSerializer(offers, many=True)
            return Response(serializer.data)
        return Response({'error': 'branch_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_master(self, request):
        """Get offers by master"""
        master_id = request.query_params.get('master_id')
        if master_id:
            offers = Offer.objects.filter(master_id=master_id)
            serializer = OfferSerializer(offers, many=True)
            return Response(serializer.data)
        return Response({'error': 'master_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_mobile(self, request):
        """Search offers by customer mobile"""
        mobile = request.query_params.get('mobile')
        if mobile:
            offers = Offer.objects.filter(customer_mobile__icontains=mobile)
            serializer = OfferSerializer(offers, many=True)
            return Response(serializer.data)
        return Response({'error': 'mobile is required'}, status=status.HTTP_400_BAD_REQUEST)


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['offer', 'person', 'call_type']
