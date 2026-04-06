from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.routers import DefaultRouter

from students.models import Student
from .models import StudentOffer, OfferRecipient, OfferNote
from .serializers import StudentOfferSerializer, OfferRecipientSerializer, OfferNoteSerializer
from .whatsapp import send_whatsapp_message


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class StudentOfferViewSet(viewsets.ModelViewSet):
    queryset = StudentOffer.objects.all()
    serializer_class = StudentOfferSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['branch', 'status', 'target_level']
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def send_offer(self, request, pk=None):
        offer = self.get_object()
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
            'offer': self.get_serializer(offer).data,
            'recipients_count': created_count,
            'email_count': email_count,
            'whatsapp_count': whatsapp_count,
        })

    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        offer = self.get_object()
        recipients = offer.recipients.all()
        serializer = OfferRecipientSerializer(recipients, many=True)
        return Response(serializer.data)


class OfferRecipientViewSet(viewsets.ModelViewSet):
    queryset = OfferRecipient.objects.all()
    serializer_class = OfferRecipientSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'student', 'channel', 'status']


class OfferNoteViewSet(viewsets.ModelViewSet):
    queryset = OfferNote.objects.all()
    serializer_class = OfferNoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['offer', 'person']

    def perform_create(self, serializer):
        serializer.save(person=self.request.user)


router = DefaultRouter()
router.register(r'student-offers', StudentOfferViewSet, basename='student-offers')
router.register(r'offer-recipients', OfferRecipientViewSet, basename='offer-recipients')
router.register(r'offer-notes', OfferNoteViewSet, basename='offer-notes')
