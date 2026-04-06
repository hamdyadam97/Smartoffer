from rest_framework import serializers
from .models import Account, AttachType, Attach, AccountAttach, AccountCondition, AccountNote
from students.serializers import StudentSerializer, StudentSimpleSerializer
from courses.serializers import CourseSerializer, CourseSimpleSerializer


class AccountSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()
    key = serializers.SerializerMethodField()
    key_rtl = serializers.SerializerMethodField()
    required_price = serializers.SerializerMethodField()
    paid_price = serializers.SerializerMethodField()
    remain_price = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'key', 'key_rtl', 'name', 'register_date',
            'course_payment_type', 'course_price', 'course_discount_amount',
            'course_profit_amount', 'course_credit_amount', 'note',
            'course', 'student', 'required_price', 'paid_price', 'remain_price',
            'last_person', 'last_person_name', 'last_update', 'created_at'
        ]
    
    def get_key(self, obj):
        return obj.get_key()
    
    def get_key_rtl(self, obj):
        return obj.get_key_rtl()
    
    def get_required_price(self, obj):
        return obj.get_required_price()
    
    def get_paid_price(self, obj):
        return obj.get_paid_price()
    
    def get_remain_price(self, obj):
        return obj.get_remain_price()
    
    def get_name(self, obj):
        return obj.student.get_full_name()
    
    def create(self, validated_data):
        student_data = validated_data.pop('student')
        contact_data = student_data.pop('contact')
        from students.models import Contact, Student
        from courses.models import Course
        
        contact = Contact.objects.create(**contact_data)
        student = Student.objects.create(contact=contact)
        
        account = Account.objects.create(student=student, **validated_data)
        return account
    
    def update(self, instance, validated_data):
        student_data = validated_data.pop('student', {})
        contact_data = student_data.pop('contact', {})
        
        # Update contact
        for attr, value in contact_data.items():
            setattr(instance.student.contact, attr, value)
        instance.student.contact.save()
        
        # Update account
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class AccountSimpleSerializer(serializers.ModelSerializer):
    student = StudentSimpleSerializer()
    course = CourseSimpleSerializer()
    key = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_mobile = serializers.CharField(source='student.contact.mobile', read_only=True)
    course_name = serializers.CharField(source='course.master.name', read_only=True)
    remain_price = serializers.SerializerMethodField()
    paid_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'key', 'name', 'register_date',
            'course_payment_type', 'course_price', 'course', 'student',
            'student_name', 'student_mobile', 'course_name', 'remain_price', 'paid_price'
        ]
    
    def get_key(self, obj):
        return obj.get_key()
    
    def get_name(self, obj):
        return obj.student.get_full_name()
    
    def get_remain_price(self, obj):
        return obj.get_remain_price()
    
    def get_paid_price(self, obj):
        return obj.get_paid_price()


class AttachTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachType
        fields = '__all__'


class AttachSerializer(serializers.ModelSerializer):
    attach_type_name = serializers.CharField(source='attach_type.name', read_only=True)
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    
    class Meta:
        model = Attach
        fields = [
            'id', 'title', 'file_data', 'file_name', 'file_type',
            'attach_type', 'attach_type_name', 'person', 'person_name', 'created_at'
        ]


class AccountAttachSerializer(serializers.ModelSerializer):
    account_key = serializers.CharField(source='account.get_key', read_only=True)
    attach_detail = AttachSerializer(source='attach', read_only=True)
    
    class Meta:
        model = AccountAttach
        fields = ['id', 'account', 'account_key', 'attach', 'attach_detail', 'created_at']


class AccountConditionSerializer(serializers.ModelSerializer):
    account_key = serializers.CharField(source='account.get_key', read_only=True)
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    
    class Meta:
        model = AccountCondition
        fields = [
            'id', 'account', 'account_key', 'person', 'person_name',
            'title', 'content', 'fulfilled', 'created_at', 'updated_at'
        ]


class AccountNoteSerializer(serializers.ModelSerializer):
    account_key = serializers.CharField(source='account.get_key', read_only=True)
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    
    class Meta:
        model = AccountNote
        fields = [
            'id', 'account', 'account_key', 'person', 'person_name',
            'content', 'created_at', 'updated_at'
        ]
