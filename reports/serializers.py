from rest_framework import serializers

from .models import ReportSnapshot


class ReportSnapshotSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_short_name', read_only=True)

    class Meta:
        model = ReportSnapshot
        fields = '__all__'
