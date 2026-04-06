from rest_framework import serializers

from .models import StudentOffer, OfferRecipient, OfferNote


class StudentOfferSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_short_name', read_only=True)

    class Meta:
        model = StudentOffer
        fields = '__all__'


class OfferRecipientSerializer(serializers.ModelSerializer):
    offer_title = serializers.CharField(source='offer.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = OfferRecipient
        fields = '__all__'


class OfferNoteSerializer(serializers.ModelSerializer):
    offer_title = serializers.CharField(source='offer.title', read_only=True)
    person_name = serializers.CharField(source='person.get_short_name', read_only=True)

    class Meta:
        model = OfferNote
        fields = '__all__'
