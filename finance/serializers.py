from rest_framework import serializers
from .models import Payment, PaymentOut, Deposit, Withdraw, BillBuyType, BillBuy, Offer, Call
from registrations.serializers import AccountSimpleSerializer


class PaymentSerializer(serializers.ModelSerializer):
    account_key = serializers.CharField(source='account.get_key', read_only=True)
    student_name = serializers.CharField(source='account.student.get_full_name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    tax = serializers.SerializerMethodField()
    amount_with_tax = serializers.SerializerMethodField()
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'code', 'date', 'amount_number', 'amount_string',
            'type', 'payment_method', 'payment_method_display', 'payment_method_code',
            'note', 'account', 'account_key', 'student_name',
            'tax', 'amount_with_tax', 'last_person', 'last_person_name',
            'last_update', 'created_at'
        ]
    
    def get_tax(self, obj):
        return obj.get_tax()
    
    def get_amount_with_tax(self, obj):
        return obj.get_amount_with_tax()


class PaymentSimpleSerializer(serializers.ModelSerializer):
    account_key = serializers.CharField(source='account.get_key', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'code', 'date', 'amount_number', 'type', 'account', 'account_key']


class PaymentOutSerializer(serializers.ModelSerializer):
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = PaymentOut
        fields = [
            'id', 'code', 'date', 'amount_number', 'amount_string',
            'receiver_name', 'reason', 'payment_method', 'payment_method_display',
            'last_person', 'last_person_name', 'last_update', 'created_at'
        ]


class DepositSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    
    class Meta:
        model = Deposit
        fields = [
            'id', 'code', 'date', 'amount', 'bank', 'bank_name',
            'note', 'last_person', 'last_person_name', 'last_update', 'created_at'
        ]


class WithdrawSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    
    class Meta:
        model = Withdraw
        fields = [
            'id', 'code', 'date', 'amount', 'bank', 'bank_name',
            'note', 'last_person', 'last_person_name', 'last_update', 'created_at'
        ]


class BillBuyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillBuyType
        fields = '__all__'


class BillBuySerializer(serializers.ModelSerializer):
    bill_buy_type_name = serializers.CharField(source='bill_buy_type.name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    net_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = BillBuy
        fields = [
            'id', 'code', 'date', 'bill_buy_type', 'bill_buy_type_name',
            'supplier', 'amount', 'tax', 'discount', 'net_amount',
            'note', 'last_person', 'last_person_name', 'last_update', 'created_at'
        ]
    
    def get_net_amount(self, obj):
        return obj.get_net_amount()


class OfferSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.name', read_only=True)
    branch_name = serializers.CharField(source='master.branch.name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    net = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'code', 'customer_name', 'customer_identity_number',
            'customer_mobile', 'customer_email', 'note', 'message_body',
            'master_payment_type', 'master_price', 'master_discount_amount',
            'master_profit_amount', 'master_credit_amount', 'send_email',
            'send_sms', 'sms_body', 'message_sid', 'registered',
            'master', 'master_name', 'branch_name', 'net', 'discount',
            'last_person', 'last_person_name', 'last_update', 'created_at'
        ]
    
    def get_net(self, obj):
        return obj.get_net()
    
    def get_discount(self, obj):
        return obj.get_discount()


class OfferSimpleSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.name', read_only=True)
    net = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'code', 'customer_name', 'customer_mobile', 'master_name',
            'master_price', 'net', 'registered', 'created_at'
        ]
    
    def get_net(self, obj):
        return obj.get_net()


class CallSerializer(serializers.ModelSerializer):
    offer_detail = OfferSimpleSerializer(source='offer', read_only=True)
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    call_type_display = serializers.CharField(source='get_call_type_display', read_only=True)
    
    class Meta:
        model = Call
        fields = [
            'id', 'offer', 'offer_detail', 'person', 'person_name',
            'call_type', 'call_type_display', 'duration', 'notes', 'created_at'
        ]
