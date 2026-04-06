from rest_framework import serializers
from .models import Master, Course
from core.serializers import BranchSerializer, MasterCategorySerializer


class MasterSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branch_code = serializers.IntegerField(source='branch.code', read_only=True)
    category_name = serializers.CharField(source='master_category.name', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    
    class Meta:
        model = Master
        fields = [
            'id', 'code', 'name', 'period', 'branch', 'branch_name', 'branch_code',
            'master_category', 'category_name', 'last_person', 'last_person_name',
            'last_update', 'created_at'
        ]


class MasterSimpleSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = Master
        fields = ['id', 'code', 'name', 'branch', 'branch_name']


class CourseSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.name', read_only=True)
    master_code = serializers.IntegerField(source='master.code', read_only=True)
    branch_name = serializers.CharField(source='master.branch.name', read_only=True)
    branch_code = serializers.IntegerField(source='master.branch.code', read_only=True)
    last_person_name = serializers.CharField(source='last_person.get_short_name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'instructor', 'company_name', 'max_student_count',
            'start_date', 'end_date', 'master', 'master_name', 'master_code',
            'branch_name', 'branch_code', 'last_person', 'last_person_name',
            'last_update', 'created_at'
        ]


class CourseSimpleSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.name', read_only=True)
    master_code = serializers.IntegerField(source='master.code', read_only=True)
    branch_name = serializers.CharField(source='master.branch.name', read_only=True)
    branch_code = serializers.IntegerField(source='master.branch.code', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'code', 'master', 'master_name', 'master_code', 'branch_name', 'branch_code']
