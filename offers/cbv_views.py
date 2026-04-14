"""
Class-Based Views for Offers App
API using Django REST Framework CBV instead of ViewSet
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from students.models import Student
from .models import StudentOffer, OfferRecipient, OfferNote
from .serializers import StudentOfferSerializer, OfferRecipientSerializer, OfferNoteSerializer
from .whatsapp import send_whatsapp_message


class IsAuthenticated(permissions.IsAuthenticated):
    pass


# ============================================================
# StudentOffer API (Class-Based Views)
# ============================================================

class StudentOfferListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/offers/student-offers/     → List all student offers
    POST /api/offers/student-offers/     → Create new student offer
    """
    queryset = StudentOffer.objects.all()
    serializer_class = StudentOfferSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['branch', 'status', 'target_level']
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StudentOfferDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/offers/student-offers/<id>/  → Retrieve student offer
    PUT    /api/offers/student-offers/<id>/  → Update student offer
    PATCH  /api/offers/student-offers/<id>/  → Partial update
    DELETE /api/offers/student-offers/<id>/  → Delete student offer
    """
    queryset = StudentOffer.objects.all()
    serializer_class = StudentOfferSerializer
    permission_classes = [IsAuthenticated]


class StudentOfferSendAPIView(APIView):
    """
    POST /api/offers/student-offers/<id>/send-offer/  → Send offer to students
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        offer = get_object_or_404(StudentOffer, pk=pk)
        user = request.user
        channel_override = request.data.get('channel')  # optional: 'email' | 'whatsapp'

        # Permission check
        if not user.is_superuser and not user.groups.filter(name='can_send_offers').exists():
            raise PermissionDenied('ليس لديك صلاحية إرسال العروض.')

        # Determine target students
        students_qs = Student.objects.all()
        if offer.target_level != 'الكل':
            students_qs = students_qs.filter(level=offer.target_level)

        created_count = 0
        email_count = 0
        whatsapp_count = 0
        for student in students_qs:
            channel = channel_override or student.preferred_contact or 'email'
            recipient, _ = OfferRecipient.objects.get_or_create(
                offer=offer,
                student=student,
                defaults={'channel': channel, 'status': 'مرسل'}
            )
            created_count += 1

            # Send email
            if channel == 'email' and student.contact.email:
                send_mail(
                    subject=offer.title,
                    message=offer.content,
                    from_email=None,
                    recipient_list=[student.contact.email],
                    fail_silently=True,
                )
                email_count += 1

            # Send WhatsApp
            if channel == 'whatsapp' and student.contact.mobile:
                send_whatsapp_message(student.contact.mobile, offer.content)
                whatsapp_count += 1

        offer.status = 'مرسلة'
        offer.sent_at = timezone.now()
        offer.save()

        return Response({
            'offer': StudentOfferSerializer(offer).data,
            'recipients_count': created_count,
            'email_count': email_count,
            'whatsapp_count': whatsapp_count,
        })


class StudentOfferRecipientsAPIView(APIView):
    """
    GET /api/offers/student-offers/<id>/recipients/  → List offer recipients
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        offer = get_object_or_404(StudentOffer, pk=pk)
        recipients = offer.recipients.all()
        serializer = OfferRecipientSerializer(recipients, many=True)
        return Response(serializer.data)


# ============================================================
# OfferRecipient API (Class-Based Views)
# ============================================================

class OfferRecipientListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/offers/offer-recipients/     → List all offer recipients
    POST /api/offers/offer-recipients/     → Create new offer recipient
    """
    queryset = OfferRecipient.objects.all()
    serializer_class = OfferRecipientSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'student', 'channel', 'status']


class OfferRecipientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/offers/offer-recipients/<id>/  → Retrieve offer recipient
    PUT    /api/offers/offer-recipients/<id>/  → Update offer recipient
    PATCH  /api/offers/offer-recipients/<id>/  → Partial update
    DELETE /api/offers/offer-recipients/<id>/  → Delete offer recipient
    """
    queryset = OfferRecipient.objects.all()
    serializer_class = OfferRecipientSerializer
    permission_classes = [IsAuthenticated]


# ============================================================
# OfferNote API (Class-Based Views)
# ============================================================

class OfferNoteListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/offers/offer-notes/     → List all offer notes
    POST /api/offers/offer-notes/     → Create new offer note
    """
    queryset = OfferNote.objects.all()
    serializer_class = OfferNoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'person']

    def perform_create(self, serializer):
        serializer.save(person=self.request.user)


class OfferNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/offers/offer-notes/<id>/  → Retrieve offer note
    PUT    /api/offers/offer-notes/<id>/  → Update offer note
    PATCH  /api/offers/offer-notes/<id>/  → Partial update
    DELETE /api/offers/offer-notes/<id>/  → Delete offer note
    """
    queryset = OfferNote.objects.all()
    serializer_class = OfferNoteSerializer
    permission_classes = [IsAuthenticated]
