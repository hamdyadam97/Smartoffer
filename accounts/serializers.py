from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Team, Person, BranchAccess, Role, EmployeeRole, EmployeePerformance
from core.models import Branch


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class BranchAccessSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = BranchAccess
        fields = ['id', 'branch', 'branch_name', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class EmployeeRoleSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = EmployeeRole
        fields = ['id', 'person', 'person_name', 'role', 'role_name', 'branch', 'branch_name', 'assigned_at']


class EmployeePerformanceSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = EmployeePerformance
        fields = [
            'id', 'person', 'person_name', 'branch', 'branch_name',
            'period_month', 'period_year', 'offers_sent', 'offers_opened',
            'offers_interacted', 'subscriptions', 'created_at', 'updated_at'
        ]


class PersonSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    branches = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    roles_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Person
        fields = [
            'id', 'email', 'first_name', 'second_name', 'third_name', 'forth_name',
            'mobile', 'phone', 'address', 'photo', 'team', 'team_name', 'branch',
            'branch_name', 'branches', 'is_staff', 'is_active', 'is_superuser',
            'full_name', 'short_name', 'roles_list', 'last_login_date', 'ip_address', 'options',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_branches(self, obj):
        return [
            {'id': b.id, 'code': b.code, 'name': b.name}
            for b in obj.get_branches()
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_short_name(self, obj):
        return obj.get_short_name()

    def get_roles_list(self, obj):
        return [
            {'id': r.id, 'role': r.role.name, 'role_display': r.role.get_name_display(), 'branch': r.branch.name}
            for r in obj.roles.select_related('role', 'branch').all()
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        person = Person.objects.create(**validated_data)
        if password:
            person.set_password(password)
            person.save()
        return person
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PersonCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Person
        fields = [
            'id', 'email', 'password', 'first_name', 'second_name', 'third_name',
            'forth_name', 'mobile', 'phone', 'address', 'team', 'branch',
            'is_staff', 'is_active', 'is_superuser'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        person = Person.objects.create(**validated_data)
        person.set_password(password)
        person.save()
        return person


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that returns user data with token"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'short_name': user.get_short_name(),
            'branch': {
                'id': user.branch.id if user.branch else None,
                'name': user.branch.name if user.branch else None,
            },
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return data
