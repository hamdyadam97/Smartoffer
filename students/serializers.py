from rest_framework import serializers
from .models import Contact, Student


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'second_name', 'third_name', 'forth_name',
            'full_name', 'short_name', 'address', 'mobile', 'phone',
            'nationality', 'identity_number', 'identity_location',
            'identity_start_date', 'birth_date', 'birth_location',
            'qualification', 'photo', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_short_name(self, obj):
        return obj.get_short_name()


class ContactSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'second_name', 'third_name', 'forth_name',
            'full_name', 'short_name', 'mobile', 'identity_number'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_short_name(self, obj):
        return obj.get_short_name()


class StudentSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    full_name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    mobile = serializers.CharField(source='contact.mobile', read_only=True)
    email = serializers.CharField(source='contact.email', read_only=True)
    first_name = serializers.CharField(source='contact.first_name', read_only=True)
    second_name = serializers.CharField(source='contact.second_name', read_only=True)
    third_name = serializers.CharField(source='contact.third_name', read_only=True)
    forth_name = serializers.CharField(source='contact.forth_name', read_only=True)
    phone = serializers.CharField(source='contact.phone', read_only=True)
    address = serializers.CharField(source='contact.address', read_only=True)
    identity_number = serializers.CharField(source='contact.identity_number', read_only=True)
    nationality = serializers.CharField(source='contact.nationality', read_only=True)
    birth_date = serializers.CharField(source='contact.birth_date', read_only=True)
    qualification = serializers.CharField(source='contact.qualification', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'contact', 'full_name', 'short_name', 'mobile', 'email',
            'first_name', 'second_name', 'third_name', 'forth_name',
            'phone', 'address', 'identity_number', 'nationality',
            'birth_date', 'qualification', 'level', 'preferred_contact',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        contact_data = validated_data.pop('contact')
        contact = Contact.objects.create(**contact_data)
        student = Student.objects.create(contact=contact, **validated_data)
        return student
    
    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact', {})
        
        # Update contact
        for attr, value in contact_data.items():
            setattr(instance.contact, attr, value)
        instance.contact.save()
        
        return instance


class StudentSimpleSerializer(serializers.ModelSerializer):
    contact = ContactSimpleSerializer()
    
    class Meta:
        model = Student
        fields = ['id', 'contact']
